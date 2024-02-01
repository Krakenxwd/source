import datetime
import os
import uuid
from statistics import mean
import json
import magic
import pandas as pd
from auditlog.models import LogEntry
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import transaction
from django.db.models import F, Count, When, Case, Q
from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode
from django.views import View
from django.views.generic import FormView, DetailView, UpdateView, ListView
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from claim_application.filters import ListDocumentFilter, ExportDocumentFilter
from claim_application.forms import UploadDocumentForm, ApplicationHolderNomineeFormSet
from claim_application.models import ApplicationDocument, SingleDocument, ReProcessDocumentEvents, PageField, Claimant, \
    ClaimantFields, PageLabel, MagicLinkHash, Export
from claim_application.tables import ListDocumentTable, SingleDocumentTable, ExportTable
from claim_application.tasks import process_document, process_single_page, run_validation_rules, export_service
from claim_application.templatetags.htmlfilter import has_group
from claim_application.utils import get_number_of_pages, get_not_deleted_or_404, get_file_size, \
    is_complete_status_or_404, excel_response, get_page_level_document_json_data, find_csv_seperator
from glib_sftp.tasks import send_processed_files_to_sftp
from master.filters import FieldScoreFilterView
from master.models import AccountConfiguration, MasterPageLabel, MasterField, MasterType, DigitalMasterField
from master.models import ExtractionConfiguration
from master.tables import FieldScoreTable
from mixins.models import User
from mixins.views import GroupRequiredMixin


# Create your views here.
class UploadDocuments(LoginRequiredMixin, GroupRequiredMixin, FormView):
    template_name = 'claim_application/upload/upload.html'
    form_class = UploadDocumentForm
    success_url = reverse_lazy('claim_application:list')
    group_required = ('admin',)
    documents_to_process = []

    def form_invalid(self, form):
        return super(UploadDocuments, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(UploadDocuments, self).get_context_data(**kwargs)
        configuration = ExtractionConfiguration.objects.first()
        context.update({
            'configuration': configuration,
            'claim_formset': ApplicationHolderNomineeFormSet(),
        })
        return context

    def create_single_document(self, *args):
        application_doc, doc_password, file_obj = args
        mime_type = magic.from_buffer(file_obj.read(1024), mime=True)
        num_pages = get_number_of_pages(file_obj, mime_type)
        name = os.path.split(file_obj.name)[1]
        size = get_file_size(file_obj.size)
        SingleDocument.objects.create(document=application_doc,
                                      type=SingleDocument.RAW,
                                      name=name,
                                      file=file_obj,
                                      size=size,
                                      mime_type=mime_type,
                                      num_pages=num_pages,
                                      created_by=self.request.user,
                                      file_password=doc_password)

    def save_claim_details(self, application_doc, post_data):
        for i in range(0, int(post_data.get('form-TOTAL_FORMS')[0])):
            claimant_object = Claimant.objects.create(
                document=application_doc,
                type=Claimant.HOLDER if post_data.get(f'form-{i}-entity_type')[0] == 'holder' else Claimant.NOMINEE,
                customer_id=post_data.get(f'form-{i}-customer_id')[0]
            )
            for field in DigitalMasterField.objects.filter(is_active=True):
                code = field.code
                print("**", f'form-{i}-{code}')
                if isinstance(post_data.get(f'form-{i}-{code}'), list) and post_data.get(f'form-{i}-{code}', []) and \
                        post_data.get(f'form-{i}-{code}')[0]:
                    if field.data_type == DigitalMasterField.TEXT:
                        ClaimantFields.objects.create(claimant=claimant_object, digital_master_field=field,
                                                      text=post_data.get(f'form-{i}-{code}')[0],
                                                      value_text=post_data.get(f'form-{i}-{code}')[0])
                    elif field.data_type == DigitalMasterField.DATE:
                        ClaimantFields.objects.create(claimant=claimant_object, digital_master_field=field,
                                                      text=post_data.get(f'form-{i}-{code}')[0],
                                                      value_date=datetime.datetime.strptime(
                                                          post_data.get(f'form-{i}-{code}')[0], '%Y-%m-%d'))

    def form_valid(self, form):
        context = self.get_context_data()
        post_data = dict(self.request.POST)
        is_exceeded_limit = False
        configuration = context['configuration']  # Extraction Configuration
        application_type_id = post_data.get('document_type')[0] if post_data.get('document_type', '') else ''
        password_list = post_data.get('password', [])

        # get the application type if available
        master_type = MasterType.objects.filter(id=application_type_id.strip()).first() if application_type_id else None
        with transaction.atomic():
            config = AccountConfiguration.objects.first()
            application_doc = ApplicationDocument.objects.create(name='merged.pdf',
                                                                 policy_number=post_data.get('policy_number', '')[0],
                                                                 configuration=configuration,
                                                                 master_type=master_type,
                                                                 created_by=self.request.user)
            self.save_claim_details(application_doc, post_data)
            for index, file in enumerate(form.files.getlist('file')):
                try:
                    doc_password = password_list[index] if password_list else ''
                    # check the limit
                    if config and config.has_upload_limit:
                        upload_limit = config.upload_limit
                        if upload_limit > 0:
                            upload_limit -= 1
                            config.upload_limit = upload_limit
                            config.save()

                            self.create_single_document(application_doc, doc_password, file)
                        else:
                            messages.warning(self.request,
                                             'Exceeded the limit for processing or permission for upload has been denied.')
                            is_exceeded_limit = True
                            break
                    else:
                        self.create_single_document(application_doc, doc_password, file)
                except Exception as e:
                    print(e)
            if application_doc:
                application_doc.log_task_submitted()
                transaction.on_commit(lambda: process_document.delay(application_doc.id))

            if is_exceeded_limit:
                application_doc.log_invalid("Exceeded the limit")
                return redirect('claim_application:upload')
        return HttpResponseRedirect(self.get_success_url())


class ListDocumentView(LoginRequiredMixin, GroupRequiredMixin, FilterView, SingleTableView):
    model = ApplicationDocument
    table_class = ListDocumentTable
    template_name = 'claim_application/list/list.html'
    filterset_class = ListDocumentFilter
    paginate_by = 25
    group_required = ('admin',)

    def get_context_data(self, **kwargs):
        context = super(ListDocumentView, self).get_context_data(**kwargs)
        context['has_filter'] = any(value for value in self.request.GET.values())
        context['first_file'] = ApplicationDocument.objects.order_by(
            'created_at').first()
        paginator, page_number, paginated_query, status = self.paginate_queryset(
            self.filterset_class(self.request.GET, queryset=ApplicationDocument.objects.all()).qs, self.paginate_by)
        context['total_documents'] = paginator.object_list.count()
        context = context | paginator.object_list.aggregate(
            queued_documents=Count(Case(When(status=ApplicationDocument.QUEUED, then=0))),
            processing_documents=Count(
                Case(When(status=ApplicationDocument.PROCESSING, then=0))),
            success_documents=Count(
                Case(When(status=ApplicationDocument.COMPLETED, then=0))),
            failed_documents=Count(Case(When(status=ApplicationDocument.ERROR, then=0))))
        context['queued_docs_list'] = list(
            ApplicationDocument.objects.filter(status=ApplicationDocument.QUEUED, id__in=paginated_query).values_list(
                'id', flat=True))
        context['processing_docs_list'] = list(ApplicationDocument.objects.filter(status=ApplicationDocument.PROCESSING,
                                                                                  id__in=paginated_query).values_list(
            'id', flat=True))
        return context


class DeleteDocumentView(LoginRequiredMixin, GroupRequiredMixin, View):
    model = ApplicationDocument
    success_url = reverse_lazy('claim_application:list')
    pk_url_kwarg = 'pk'
    group_required = ('admin',)

    def __init__(self, *args, **kwargs):
        super(DeleteDocumentView, self).__init__(*args, **kwargs)
        self.object = None

    def get_object(self, *args, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.model.objects.filter(id=pk)
        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                ("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object(*args, **kwargs)
        success_url = self.get_success_url()
        if request.user.is_superuser:
            self.object.delete()
        else:
            self.object.status = ApplicationDocument.DELETED
            self.object.save()
        return HttpResponseRedirect(success_url)

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def get_success_url(self):
        if self.success_url:
            return self.success_url.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")


class AnalyticsView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    template_name = 'claim_application/analytics/analytics.html'
    group_required = ('admin',)
    model = ApplicationDocument

    def get_queryset(self):
        queryset = super(AnalyticsView, self).get_queryset()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AnalyticsView, self).get_context_data(**kwargs)
        query = self.object_list
        context['first_file'] = query.last()
        try:
            context['datetime_set'] = True
            date_range = self.request.GET.get('datetime', '').split('-')
            start_date = date_range[0].strip()
            end_date = date_range[1].strip()
            start_date = datetime.datetime.combine(datetime.datetime.strptime(start_date, '%d/%m/%Y'),
                                                   datetime.time.min)
            end_date = datetime.datetime.combine(datetime.datetime.strptime(end_date, '%d/%m/%Y'), datetime.time.max)
        except Exception as e:
            print("Error: ", e)
            context['datetime_set'] = False
            today_datetime = datetime.datetime.now()
            start_date = datetime.datetime.combine(today_datetime, datetime.time.min)
            end_date = datetime.datetime.combine(today_datetime, datetime.time.max)
        context['start_date'] = start_date
        context['end_date'] = end_date
        query = query.filter(created_at__range=[start_date, end_date])
        page_label_query = PageLabel.objects.filter(created_at__range=[start_date, end_date])
        context['total_count'] = query.count()
        context['total_pages'] = sum(
            list(query.filter().values_list("num_pages", flat=True)))
        context['total_processed_count'] = query.filter(status=ApplicationDocument.COMPLETED,
                                                        job_started_at__isnull=False,
                                                        job_completed_at__isnull=False).count()
        context['total_failed_count'] = query.filter(status__in=[ApplicationDocument.QUEUED,
                                                                 ApplicationDocument.PROCESSING,
                                                                 ApplicationDocument.ERROR]).count()
        document_total_timing = []
        page_total_timing = []
        for timing in query.filter(status=ApplicationDocument.COMPLETED, job_started_at__isnull=False,
                                   job_completed_at__isnull=False) \
                .values_list('job_started_at', 'job_completed_at', 'num_pages', 'id'):
            t = (timing[1] - timing[0]).seconds
            document_total_timing.append(t)
            page_total_timing.append(t / timing[2]) if timing[2] > 0 else page_total_timing.append(0)
        context['avg_processing_time_doc'] = round(
            mean(document_total_timing if document_total_timing else [0]), 2)
        context['avg_processing_time_page'] = round(
            mean(page_total_timing if page_total_timing else [0]), 2)
        context['pie_chart_user_documents'] = self.get_pie_documents_user(query)
        context['pie_chart_document_status'] = self.get_pie_documents_status(query)
        context['pie_chart_document_master_type'] = self.get_pie_documents_master_type(query)
        context['spline_chart_processed_documents'] = self.get_spline_chart_processed_documents(query)
        context['pie_chart_page_labels'] = self.get_pie_documents_page_labels(page_label_query)
        return context

    def get_pie_documents_user(self, query):
        results = list(query.filter(created_by__isnull=False).order_by('created_by').values('created_by').annotate(
            created_by_count=Count('created_by'))
                       .values_list("created_by__email", "created_by_count"))
        send_obj = [{"name": x[0], "y": x[1]} for x in results]
        return send_obj

    def get_pie_documents_status(self, query):
        return [{'name': x[0], 'y': x[1]} for x in list(query.order_by('status').values('status').annotate(
            y=Count('status'), name=F('status')).values_list('name', 'y'))]

    def get_pie_documents_master_type(self, query):
        return [{'name': x[0], 'y': x[1]} for x in list(query.order_by('master_type').values('master_type').annotate(
            y=Count('master_type'), name=F('master_type__name')).values_list('name', 'y'))]

    def get_pie_documents_page_labels(self, page_label_query):
        return [{'name': x[0], 'y': x[1]} for x in list(
            page_label_query.values('master_page_label').order_by('master_page_label').annotate(
                name=F('master_page_label__name'), total=Count('master_page_label')).values_list('name', 'total'))]

    def get_spline_chart_processed_documents(self, query):
        send_obj = []
        for status in ApplicationDocument.STATUS_CHOICES:
            send_obj.append({
                'name': status[1],
                'data': [{f'{x[0].strftime("%Y/%m/%d")}': f'{x[1]}'} for x in
                         list(query.filter(status=status[0])
                              .order_by('created_at')
                              .values('created_at')
                              .annotate(y=Count('created_at'), name=F('created_at'))
                              .values_list('name', 'y'))]
            })

        result = []

        for document_status_dict in send_obj:
            temp_dict = {'name': document_status_dict['name'], 'data': {}}

            for data_dict in document_status_dict['data']:
                for date_key, value in data_dict.items():
                    if date_key in temp_dict['data']:
                        temp_dict['data'][date_key] += int(value)
                    else:
                        temp_dict['data'][date_key] = int(value)

            result.append(temp_dict)

        result = sorted(result, key=lambda x: x['name'])

        return result


class AnalyticsExportView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ('admin',)

    def post(self, *args, **kwargs):
        data = dict(self.request.POST)
        data.pop('csrfmiddlewaretoken')
        date_range = data.pop('export-reportrange')[0].replace(' ', '')
        header = ['Total Documents', 'Avg. Processing Time Per Page', 'Processed Files', 'Unprocessed Files',
                  'Total Pages']
        result = [x[0] for x in list(data.values())]
        df = pd.DataFrame({'Field Headers': header, 'Result': result})
        output_file = "export-analytics-{}-{}".format(uuid.uuid4().hex[0:7], date_range)
        return excel_response(df, output_file, 'Analytics Export')


class DetailSummary(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = ApplicationDocument
    context_object_name = 'document'
    template_name = 'claim_application/detail/detail_summary.html'
    group_required = ('admin',)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser and self.get_object().status == ApplicationDocument.DELETED:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailSummary, self).get_context_data(**kwargs)
        context['files_count'] = SingleDocument.objects.filter(
            document=self.kwargs.get('pk'), type=SingleDocument.RAW).count()
        return context


class MagicLinkDetailSummary(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = ApplicationDocument
    context_object_name = 'document'
    template_name = 'claim_application/detail/magic_template.html'
    group_required = ('apiuser',)
    pk_url_kwarg = 'key'
    object = None

    def get_object(self, queryset=None):
        return self.object

    def dispatch(self, request, *args, **kwargs):
        mhash = self.kwargs.get(self.pk_url_kwarg, None)
        if mhash is None:
            raise AttributeError("magic hash is not available.")

        try:
            hash_obj = get_object_or_404(MagicLinkHash, magic_hash=mhash)
            self.object = hash_obj.document

            # Logged in a hash user
            login(request, hash_obj.user, backend='allauth.account.auth_backends.AuthenticationBackend')

            # Destroy a magic link hash once hit the server
            hash_obj.delete()

            return super(MagicLinkDetailSummary, self).dispatch(request, *args, **kwargs)
        except Exception:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(MagicLinkDetailSummary, self).get_context_data(**kwargs)
        return context


class DetailSummaryFiles(LoginRequiredMixin, GroupRequiredMixin, SingleTableView):
    model = SingleDocument
    table_class = SingleDocumentTable
    template_name = 'claim_application/detail/detail_files.html'
    group_required = ('admin',)

    def get_queryset(self):
        queryset = super(DetailSummaryFiles, self).get_queryset().filter(
            document=ApplicationDocument.objects.get(id=self.kwargs.get('pk')), type=SingleDocument.RAW)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DetailSummaryFiles, self).get_context_data(**kwargs)
        context['document'] = ApplicationDocument.objects.get(id=self.kwargs.get('pk'))
        return context


class DetailSummaryEvents(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = ApplicationDocument
    context_object_name = 'document'
    template_name = 'claim_application/detail/detail_events.html'
    group_required = ('admin',)


class DetailEdit(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = ApplicationDocument
    context_object_name = 'document'
    template_name = 'claim_application/detail/detail_edit.html'
    group_required = ('admin',)

    def get_context_data(self, **kwargs):
        context = super(DetailEdit, self).get_context_data(**kwargs)
        page_num = [self.request.GET.get('pagenumber')] if self.request.GET.get('pagenumber', '') else []
        context['page_num'] = page_num[0] if any(
            int(x) in list(self.get_object().pages.all().values_list('number', flat=True)) for x in page_num) else 1
        context['labels'] = MasterPageLabel.objects.filter(is_active=True, type=self.get_object().master_type)
        return context


class RerunProcessView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = ApplicationDocument
    group_required = ('admin',)

    def get_object(self, queryset=None):
        if self.request.user.is_superuser:
            obj = get_object_or_404(ApplicationDocument, Q(
                pk=self.kwargs['pk']) & ~Q(status=ApplicationDocument.QUEUED))
        else:
            obj = get_not_deleted_or_404(ApplicationDocument, Q(
                pk=self.kwargs['pk']) & ~Q(status=ApplicationDocument.QUEUED))
        return obj

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        document = self.get_object(ApplicationDocument)
        params_dict = request.GET.dict()

        # check ApplicationDocument rerun logs.
        if document.re_run_events.filter(status=ReProcessDocumentEvents.OPEN).count() > 0:
            messages.warning(request,
                             'Document is already in processing; please wait until we are finished with the process.!!')
        else:
            print(" pass doc to process & Open ticket ")
            document.status = ApplicationDocument.QUEUED
            document.save()
            ReProcessDocumentEvents.objects.create(
                document=document, status=ReProcessDocumentEvents.OPEN)
            process_document.delay(document.id)
        url = reverse('claim_application:list')
        {k: (v.strip() if v != '' else params_dict.pop(k))
         for k, v in request.GET.dict().items()}
        if params_dict:
            url += '?' + urlencode(params_dict)
        return redirect(url)


class RerunValidationView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = ApplicationDocument
    group_required = ('admin',)

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        params_dict = request.GET.dict()

        document = is_complete_status_or_404(ApplicationDocument, Q(
            pk=self.kwargs['pk']))

        run_validation_rules.delay(document.id)

        url = reverse('claim_application:list')
        {k: (v.strip() if v != '' else params_dict.pop(k))
         for k, v in request.GET.dict().items()}
        if params_dict:
            url += '?' + urlencode(params_dict)
        return redirect(url)


class DocumentAuditReportView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    template_name = 'claim_application/audit_report/audit_report.html'
    group_required = ('',)
    model = LogEntry

    def get_queryset(self, *args, **kwargs):
        queryset = LogEntry.objects.get_for_model(ApplicationDocument).filter(object_pk=self.kwargs.get('pk')).values()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DocumentAuditReportView, self).get_context_data(**kwargs)
        return context


class UserAuditReportView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    template_name = 'claim_application/audit_report/audit_report.html'
    group_required = ('',)
    model = LogEntry

    def get_queryset(self, *args, **kwargs):
        queryset = LogEntry.objects.get_for_model(User).filter(object_pk=self.kwargs.get('pk')).values()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UpdateDocument(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    group_required = ('admin',)
    success_url = reverse_lazy('claim_applciation:detail.edit')

    def get_object(self, queryset=None):
        pk = self.kwargs['pk']
        if self.request.user.is_superuser:
            obj = ApplicationDocument.objects.filter(pk=pk).first()
        else:
            obj = ApplicationDocument.objects.filter(pk=pk).exclude(
                status=ApplicationDocument.DELETED).first()

        if obj:
            return obj
        else:
            raise Http404(
                "No %s matches the given query." % ApplicationDocument._meta.object_name
            )

    def post(self, request, *args, **kwargs):
        document = self.get_object()
        re_process_page = []

        data = {}
        page_data = {}
        for key, value in request.POST.items():
            if key.startswith('csrf'):
                continue
            tokens = key.split('-')
            if tokens[0] == "pagefield":
                page_num = int(tokens[1])
                input_type = tokens[-1]
                field_code = tokens[2]
                if page_num not in data:
                    data[page_num] = {}
                if field_code not in data[page_num]:
                    data[page_num][field_code] = {}
                data[page_num][field_code][input_type] = value
            elif tokens[0] == "page":
                page_num = int(tokens[1])
                input_type = tokens[-1]
                page_id = int(tokens[2])
                if page_num not in page_data:
                    page_data[page_num] = {}
                if page_id not in page_data[page_num]:
                    page_data[page_num][page_id] = {}
                page_data[page_num][page_id][input_type] = value
        with transaction.atomic():
            for page_num in page_data.keys():
                page = document.pages.get(number=page_num)
                if int(page_data[page_num][page.id]['changed']):
                    label = page.page_labels.first()
                    page_data[page_num][page.id]['changed'] = label.master_page_label.id != int(
                        page_data[page_num][page.id]['value'])
                    if label.master_page_label.id != int(page_data[page_num][page.id]['value']):
                        label.master_page_label = MasterPageLabel.objects.get(
                            id=int(page_data[page_num][page.id]['value']))
                        label.save()
                        print("Changed label for page %s" % page_num)
                        re_process_page.append(page)

            for page_num, item in data.items():
                page = document.pages.get(number=page_num)
                if int(page_data[page_num][page.id]['changed']):
                    continue
                for field_code, values in item.items():
                    if int(values['changed']):
                        master_field = MasterField.objects.get(
                            code=field_code, page_label=page.page_labels.first().master_page_label)
                        try:
                            page_field = PageField.objects.get(
                                page=page, field=master_field)
                        except Exception as e:
                            print("Error: ", str(e))
                            page_field = PageField.objects.filter(
                                page=page, master_field=master_field).first()
                            PageField.objects.filter(page=page, master_field=master_field).exclude(
                                id=page_field.id).delete()
                        for key, value in values.items():
                            if key == 'value':
                                data_type = master_field.data_type
                                if data_type == MasterField.TEXT:
                                    page_field.value_text = value[0:1000]
                                elif data_type == MasterField.AMOUNT:
                                    try:
                                        page_field.value_amount = float(value)
                                    except Exception as e:
                                        print("Error: ", str(e))
                                        page_field.value_amount = None
                                elif data_type == MasterField.DATE:
                                    if value:
                                        try:
                                            page_field.value_date = value
                                        except Exception as e:
                                            print(e)
                                    else:
                                        page_field.value_date = None
                            elif key == 'wmin':
                                page_field.w_min = float(value)
                            elif key == 'wmax':
                                page_field.w_max = float(value)
                            elif key == 'hmin':
                                page_field.h_min = float(value)
                            elif key == 'hmax':
                                page_field.h_max = float(value)
                            elif key == 'changed':
                                value = int(value)
                                if value:
                                    page_field.is_validated = True
                                    page_field.modified_by = request.user
                        page_field.save()

        if len(re_process_page) > 0:
            document.is_processed = False
            document.save()

        for process_page in re_process_page:
            process_single_page.delay(process_page.document.id, process_page.id)

        document.marked_for_reviewed = True
        document.modified_by = self.request.user
        document.save()
        document.refresh_from_db()

        return redirect(reverse('claim_application:detail.edit', kwargs={'pk': self.get_object().id}))


class ApproveView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    group_required = ('admin',)

    def get_redirect_url(self, **kwargs):
        if self.request.GET.get('view') and self.request.GET.get('view') == 'magic_detail':
            return reverse("claim_application:magic.detail.summary", kwargs={"pk": self.kwargs.get('pk')})
        return reverse("claim_application:detail.summary", kwargs={"pk": self.kwargs.get('pk')})

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        document = is_complete_status_or_404(ApplicationDocument, pk=self.kwargs['pk'])
        document.marked_for_reviewed = True
        document.validation_status = ApplicationDocument.APPROVED
        document.save()
        return redirect(self.get_redirect_url(**kwargs))


class RejectView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    group_required = ('admin',)

    def get_redirect_url(self, **kwargs):
        if self.request.GET.get('view') and self.request.GET.get('view') == 'magic_detail':
            return reverse("claim_application:magic.detail.summary", kwargs={"pk": self.kwargs.get('pk')})
        return reverse("claim_application:detail.summary", kwargs={"pk": self.kwargs.get('pk')})

    @transaction.atomic
    def get(self, request, *args, **kwargs):
        document = is_complete_status_or_404(ApplicationDocument, pk=self.kwargs['pk'])
        document.marked_for_reviewed = True
        document.validation_status = ApplicationDocument.REJECTED
        document.save()
        return redirect(self.get_redirect_url(**kwargs))


class DetailExcelReport(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = ApplicationDocument
    group_required = ('admin',)

    def post(self, request, *args, **kwargs):
        data = []
        document = self.get_object()
        data += get_page_level_document_json_data(document.id)
        df = pd.json_normalize(data)
        df.fillna('', inplace=True)
        sheet_name = 'Export Document Summary'
        output_file = "{}-export-{}-{}".format('sbi', document.policy_number,
                                               document.master_type.code if document.master_type else '')
        response = excel_response(df, output_file, sheet_name)
        return response


class SettingsView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = 'claim_application/settings/settings.html'

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)
        context['master_fields'] = MasterField.objects.filter(is_active=True, )
        context['master_page_labels'] = MasterPageLabel.objects.filter(~Q(code='other'), is_active=True)
        context['master_types'] = MasterType.objects.filter(is_active=True)
        context['digital_master_fields'] = DigitalMasterField.objects.filter(is_active=True)
        context['extraction_configuration'] = ExtractionConfiguration.objects.first()
        context['set_field_scores'] = DigitalMasterField.objects.all()
        return context


class HTMXFetchMasterField(LoginRequiredMixin, GroupRequiredMixin, View):
    template_name = 'claim_application/htmx/field_arranger_partial.html'
    group_required = ('admin',)

    def get(self, request, *args, **kwargs):
        context = {}
        page_label = self.kwargs.get('page_label')
        context['page_label'] = page_label
        context['master_page_labels'] = MasterField.objects.filter(page_label__code=page_label)
        context['original_order'] = ExtractionConfiguration.objects.first().get_masterfield_order().filter(
            id__in=MasterField.objects.filter(page_label__code='passport').values_list('id', flat=True))
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        try:
            new_order = request.POST.get('order[]').split(',')
            for index, value in enumerate(new_order):
                obj = MasterField.objects.get(id=value)
                obj._order = index
                obj.save()
            messages.success(self.request,
                             'Fields order has been updated successfully.')
            return HttpResponseRedirect(reverse('claim_application:settings'))
        except Exception as e:
            print(e)
            messages.error(self.request,
                           'There was an error while updating the fields order.')
            return HttpResponseRedirect(reverse('claim_application:settings'))


class HTMXFetchValidations(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    template_name = 'claim_application/htmx/validations_sidebar.html'
    model = ApplicationDocument
    context_object_name = 'document'
    group_required = ('admin',)

    def get_context_data(self, **kwargs):
        context = super(HTMXFetchValidations, self).get_context_data(**kwargs)
        return context


class HTMXFetchPolicyDigitalData(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    template_name = 'claim_application/htmx/policy_entity_sidebar.html'
    model = ApplicationDocument
    context_object_name = 'document'
    group_required = ('admin',)

    def get_context_data(self, **kwargs):
        context = super(HTMXFetchPolicyDigitalData, self).get_context_data(**kwargs)
        return context


class HTMXFetchDocumentEvents(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    template_name = 'claim_application/htmx/detail_events.html'
    model = ApplicationDocument
    context_object_name = 'document'
    group_required = ('admin',)

    def get_context_data(self, **kwargs):
        context = super(HTMXFetchDocumentEvents, self).get_context_data(**kwargs)
        return context


class HTMXFetchDocumentTable(LoginRequiredMixin, GroupRequiredMixin, SingleTableView):
    template_name = 'claim_application/htmx/document_table.html'
    model = ApplicationDocument
    context_object_name = 'document'
    group_required = ('admin',)
    table_class = ListDocumentTable
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(HTMXFetchDocumentTable, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        processing_docs_ids = self.request.GET.get('processing').split(',') if self.request.GET.get(
            'processing') else []
        queued_docs_ids = self.request.GET.get('queued').split(',') if self.request.GET.get('queued') else []
        total_count_of_processing_docs = ApplicationDocument.objects.filter(
            status=ApplicationDocument.PROCESSING).count()
        total_count_of_queued_docs = ApplicationDocument.objects.filter(status=ApplicationDocument.QUEUED).count()
        total_count_of_success_docs = ApplicationDocument.objects.filter(status=ApplicationDocument.COMPLETED).count()
        total_count_of_failed_docs = ApplicationDocument.objects.filter(status=ApplicationDocument.ERROR).count()
        call_ajax = False
        processing_docs_response = []
        processing_docs = ApplicationDocument.objects.filter(id__in=processing_docs_ids)
        for processing_doc in processing_docs:
            if processing_doc.status == ApplicationDocument.PROCESSING or processing_doc.status == ApplicationDocument.QUEUED:
                call_ajax = True
            processing_docs_response.append(fetch_response_json(processing_doc.id))

        queued_docs_response = []
        queued_docs = ApplicationDocument.objects.filter(id__in=queued_docs_ids)
        for queued_doc in queued_docs:
            if queued_doc.status == ApplicationDocument.QUEUED or queued_doc.status == ApplicationDocument.PROCESSING:
                call_ajax = True
            queued_docs_response.append(fetch_response_json(queued_doc.id))

        return JsonResponse(
            {
                'total_count_of_processing_docs': total_count_of_processing_docs,
                'total_count_of_queued_docs': total_count_of_queued_docs,
                'total_count_of_success_docs': total_count_of_success_docs,
                'total_count_of_failed_docs': total_count_of_failed_docs,
                'processing_docs_response': processing_docs_response,
                'queued_docs_response': queued_docs_response,
                'call_ajax': call_ajax
            }
        )


def fetch_response_json(document_id):
    document = ApplicationDocument.objects.get(id=document_id)
    return {
        'document_id': document.id,
        'status_html': render_to_string('claim_application/table/document_status.html', context={'record': document}),
        'actions_html': render_to_string('claim_application/table/document_action.html', context={'record': document}),
        'checkbox_html': render_to_string('claim_application/table/document_checkbox.html', context={'record': document}),
    }


class FieldScoreView(LoginRequiredMixin, GroupRequiredMixin, FilterView, SingleTableView):
    model = DigitalMasterField
    table_class = FieldScoreTable
    filterset_class = FieldScoreFilterView
    template_name = 'claim_application/settings/field_scores/list.html'
    paginate_by = 25
    group_required = ('admin',)

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(is_active=True).order_by('-created_at')
        return query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        f = self.filterset_class(self.request.GET, queryset=self.get_queryset())
        context['filter'] = f
        context['has_filter'] = any(field in self.request.GET for field in set(f.get_fields()))
        return context


class ChangeFieldScoreValueView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ('admin',)

    def get(self, request, *args, **kwargs):
        try:
            data = {}
            code = 1
            message = ''
            field_id = request.GET.get('fieldId')
            field_value = int(float(request.GET.get('fieldValue')))
            if field_value > 100:
                raise Exception('Field score value should be less than 100.')
            field_object = DigitalMasterField.objects.filter(id=field_id)
            if field_object.exists():
                field_object = field_object.first()
                field_object.expected_score = field_value
                field_object.save()
                message = f'{field_object.name} field score updated successfully.'
            else:
                code = 0
                message = 'Field not found.'
        except Exception as e:
            data['code'] = 0
            data['message'] = str(e)
            return JsonResponse(data)
        data['code'] = code
        data['message'] = message
        return JsonResponse(data)


class ChangeFieldScoreActiveStatusView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ('admin',)

    def get(self, request, *args, **kwargs):
        try:
            data = {}
            code = 1
            message = ''
            field_id = request.GET.get('fieldId')
            field_active = True if request.GET.get('fieldActive') == 'true' else False
            field_object = DigitalMasterField.objects.filter(id=field_id)
            if field_object.exists():
                field_object = field_object.first()
                field_object.do_scoring = field_active
                field_object.save()
                message = f'{field_object.name} status updated successfully.'
            else:
                code = 0
                message = 'Field not found.'
        except Exception as e:
            data['code'] = 0
            data['message'] = str(e)
            return JsonResponse(data)
        data['code'] = code
        data['message'] = message
        return JsonResponse(data)


class ExportListView(LoginRequiredMixin, GroupRequiredMixin, FilterView, SingleTableView):
    model = Export
    table_class = ExportTable
    template_name = 'claim_application/export/export.html'
    filterset_class = ExportDocumentFilter
    table_pagination = {'per_page': 25}
    group_required = ('admin',)

    def get_queryset(self):
        query = super(ExportListView, self).get_queryset()
        if not (self.request.user.is_superuser or has_group(self.request.user, 'admin')):
            query = query.filter(created_by=self.request.user)
        return query.order_by('-created_at')

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        date_range = request.POST.get('export_date_range').split('-')
        output_type = request.POST.get('output_type')
        file_type = request.POST.get('file_type')
        start_date = date_range[0].strip()
        end_date = date_range[1].strip()
        export = Export.objects.create(start_date=datetime.datetime.strptime(start_date, '%d/%m/%Y %I:%M:%S %p'),
                                       end_date=datetime.datetime.strptime(
                                           end_date, '%d/%m/%Y %I:%M:%S %p'),
                                       created_by=request.user, output_type=output_type,
                                       file_type=file_type,
                                       csv_seperator=find_csv_seperator())
        transaction.on_commit(lambda: export_service.delay(export.id))
        return redirect(reverse('claim_application:export'))

    def get_context_data(self, **kwargs):
        context = super(ExportListView, self).get_context_data(**kwargs)
        f = context['filter']
        has_filter = any(
            field in self.request.GET for field in set(f.get_fields()))
        context['has_filter'] = has_filter
        context['queued_export_list'] = list(
            Export.objects.filter(status=Export.QUEUED, id__in=f.qs).values_list('id', flat=True))
        context['processing_export_list'] = list(
            Export.objects.filter(status=Export.PROCESSING, id__in=f.qs).values_list('id', flat=True))
        if not (self.request.user.is_superuser or has_group(self.request.user, 'admin')):
            context['first_file'] = ApplicationDocument.objects.filter(
                created_by=self.request.user).order_by('created_at').first()
        else:
            context['first_file'] = ApplicationDocument.objects.order_by(
                'created_at').first()
        context['export_first_file'] = Export.objects.order_by(
            'created_at').first()
        return context

class HTMXFetchExportTable(LoginRequiredMixin, GroupRequiredMixin, View):
    template_name = 'claim_application/htmx/document_table.html'
    model = Export
    context_object_name = 'document'
    group_required = ('admin',)

    def get_context_data(self, **kwargs):
        context = super(HTMXFetchExportTable, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        porcessing_export_ids = self.request.GET.get('processing').split(',') if self.request.GET.get(
            'processing') else []
        queued_export_ids = self.request.GET.get('queued').split(',') if self.request.GET.get('queued') else []
        total_count_of_processing_export = Export.objects.filter(
            status=Export.PROCESSING).count()
        total_count_of_queued_export = Export.objects.filter(status=Export.QUEUED).count()
        call_ajax = False
        processing_export_response = []
        processing_exports = Export.objects.filter(id__in=porcessing_export_ids)
        for processing_export in processing_exports:
            if processing_export.status == Export.PROCESSING or processing_export.status == Export.QUEUED:
                call_ajax = True
            processing_export_response.append(fetch_export_response_json(processing_export.id))

        queued_export_response = []
        queued_exports = Export.objects.filter(id__in=queued_export_ids)
        for queued_export in queued_exports:
            if queued_export.status == Export.QUEUED or queued_export.status == Export.PROCESSING:
                call_ajax = True
            queued_export_response.append(fetch_export_response_json(queued_export.id))

        return JsonResponse(
            {
                'total_count_of_processing_export': total_count_of_processing_export,
                'total_count_of_queued_export': total_count_of_queued_export,
                'processing_export_response': processing_export_response,
                'queued_export_response': queued_export_response,
                'call_ajax': call_ajax
            }
        )

def fetch_export_response_json(export_id):
    export = Export.objects.get(id=export_id)
    return {
        'export_id': export.id,
        'status_html': render_to_string('claim_application/table/export/export_status.html', context={'record': export}),
        'actions_html': render_to_string('claim_application/table/export/export_action.html', context={'record': export}),
    }

class BatchDeleteDocumentsView(LoginRequiredMixin, GroupRequiredMixin, View):
    """
    View for deleting multiple documents at once.
    """

    def post(self, *args, **kwargs):
        try:
            body_unicode = self.request.body.decode('utf-8')
            received_json = json.loads(body_unicode)
            document_ids = received_json.get('documents', [])
            reload_page = False

            if not (0 < len(document_ids) < 10):
                return JsonResponse(
                    {
                        'status': 'failed',
                        'message': 'Invalid no. of documents selected. Please select between 1 to 10 documents at a time.',
                        'reload_page': reload_page,
                        'document_ids': document_ids,
                    }
                )
            
            documents_to_be_deleted = ApplicationDocument.objects.filter(id__in=document_ids)

            if not documents_to_be_deleted.exists():
                return JsonResponse(
                    {
                        'status': 'failed',
                        'message': 'No documents found matching the IDs.',
                        'reload_page': reload_page,
                        'document_ids': document_ids,
                    }
                )
            
            if documents_to_be_deleted.filter(status__in=[ApplicationDocument.PROCESSING, ApplicationDocument.QUEUED]).exists():
                return JsonResponse(
                    {
                        'status': 'failed',
                        'message': 'Cannot delete processing documents or documents in queue.',
                        'reload_page': reload_page,
                        'document_ids': document_ids,
                    }
                )
            
            if self.request.user.is_superuser:
                documents_to_be_deleted.delete()
                reload_page = True
            else:
                documents_to_be_deleted.update(status=ApplicationDocument.DELETED)
            
            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'Documents deleted successfully.',
                    'reload_page': reload_page,
                    'document_ids': document_ids,
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    'status': 'failed',
                    'message': 'Oops. An unexpected error occurred.',
                    'reload_page': reload_page,
                    'document_ids': document_ids,
                }
            )

class BatchReRunValidationsView(LoginRequiredMixin, GroupRequiredMixin, View):
    """
    View for re running validations on multiple documents at once.
    """

    group_required = ('admin',)

    def post(self, *args, **kwargs):
        try:
            body_unicode = self.request.body.decode('utf-8')
            received_json = json.loads(body_unicode)
            document_ids = received_json.get('documents', [])
            reload_page = False

            if not (0 < len(document_ids) < 10):
                return JsonResponse(
                    {
                        'status': 'failed',
                        'message': 'Invalid no. of documents selected. Please select between 1 to 10 documents at a time.',
                        'reload_page': reload_page,
                        'document_ids': document_ids,
                    }
                )
            
            documents_to_rerun_validations = ApplicationDocument.objects.filter(id__in=document_ids)

            if not documents_to_rerun_validations.exists():
                return JsonResponse(
                    {
                        'status': 'failed',
                        'message': 'No documents found matching the IDs.',
                        'reload_page': reload_page,
                        'document_ids': document_ids,
                    }
                )
            
            for document in documents_to_rerun_validations:
                run_validation_rules.delay(document.id)
            
            reload_page = True
            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'Documents queued for re-running validations successfully.',
                    'reload_page': reload_page,
                    'document_ids': document_ids,
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    'status': 'failed',
                    'message': 'Oops. An unexpected error occurred.',
                    'reload_page': reload_page,
                    'document_ids': document_ids,
                }
            )

class BatchReRunDocumentsView(LoginRequiredMixin, GroupRequiredMixin, View):
    """
    View for re running validations on multiple documents at once.
    """

    group_required = ('admin',)

    def get_object(self, queryset=None):
        if self.request.user.is_superuser:
            obj = get_object_or_404(ApplicationDocument, Q(
                pk=self.kwargs['pk']) & ~Q(status=ApplicationDocument.QUEUED))
        else:
            obj = get_not_deleted_or_404(ApplicationDocument, Q(
                pk=self.kwargs['pk']) & ~Q(status=ApplicationDocument.QUEUED))
        return obj

    @transaction.atomic
    def post(self, *args, **kwargs):
        try:
            body_unicode = self.request.body.decode('utf-8')
            received_json = json.loads(body_unicode)
            document_ids = received_json.get('documents', [])
            reload_page = False
            
            if not (0 < len(document_ids) < 10):
                return JsonResponse(
                    {
                        'status': 'failed',
                        'message': 'Invalid no. of documents selected. Please select between 1 to 10 documents at a time.',
                        'reload_page': reload_page,
                        'document_ids': document_ids,
                    }
                )
            
            documents_to_rerun = ApplicationDocument.objects.filter(id__in=document_ids)
            
            if not documents_to_rerun.exists():
                return JsonResponse(
                    {
                        'status': 'failed',
                        'message': 'No documents found matching the IDs.',
                        'reload_page': reload_page,
                        'document_ids': document_ids,
                    }
                )
            
            if documents_to_rerun.filter(status__in=[ApplicationDocument.PROCESSING, ApplicationDocument.QUEUED]).exists():
                return JsonResponse(
                    {
                        'status': 'failed',
                        'message': 'Cannot re run on queued or processing documents.',
                        'reload_page': reload_page,
                        'document_ids': document_ids,
                    }
                )
            
            for document in documents_to_rerun:
                if document.re_run_events.filter(status=ReProcessDocumentEvents.OPEN).count() > 0:
                    return JsonResponse(
                        {
                            'status': 'failed',
                            'message': 'Document is already in processing; please wait until we are finished with the process.',
                            'reload_page': reload_page,
                            'document_ids': document_ids,
                        }
                    )
                else:
                    document.status = ApplicationDocument.QUEUED
                    document.save()
                    ReProcessDocumentEvents.objects.create(
                        document=document, status=ReProcessDocumentEvents.OPEN)
                    process_document.delay(document.id)
                    reload_page = True
            
            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'Documents queued for re-run successfully.',
                    'reload_page': reload_page,
                    'document_ids': document_ids,
                }
            )
        except Exception as e:
            return JsonResponse(
                {
                    'status': 'failed',
                    'message': 'Oops. An unexpected error occurred.',
                    'reload_page': reload_page,
                    'document_ids': document_ids,
                }
            )