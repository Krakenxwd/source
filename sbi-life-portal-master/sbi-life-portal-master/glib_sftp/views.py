from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import UpdateView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from glib_sftp.forms import CreateSFTPConfigurationForm
from glib_sftp.models import SFTPConfiguration, SFTPRequest
from glib_sftp.tables import SFTPConfigurationTable, SFTPFilter, SftpEventFilter, SftpEventTable
from master.models import AccountConfiguration
from mixins.views import GroupRequiredMixin


# Create your views here.

class OverViewSftp(LoginRequiredMixin, GroupRequiredMixin, FilterView, SingleTableView):
    model = SFTPConfiguration
    table_class = SFTPConfigurationTable
    template_name = 'glib_sftp/sftp_display.html'
    filterset_class = SFTPFilter

    def dispatch(self, request, *args, **kwargs):
        if AccountConfiguration.objects.first().show_sftp:
            return super(OverViewSftp, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get_queryset(self):
        query = super(OverViewSftp, self).get_queryset()
        query = query.order_by('-created_at')
        return query

    def get_context_data(self, **kwargs):
        context = super(OverViewSftp, self).get_context_data(**kwargs)
        f = context['filter']
        has_filter = any(
            field in self.request.GET for field in set(f.get_fields()))
        context['has_filter'] = has_filter
        context['total_sftp'] = SFTPConfiguration.objects.count()
        return context


class CreateSftp(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = SFTPConfiguration
    form_class = CreateSFTPConfigurationForm
    template_name = 'glib_sftp/sftp_create.html'

    def dispatch(self, request, *args, **kwargs):
        if AccountConfiguration.objects.first().show_sftp:
            return super(CreateSftp, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get_success_url(self):
        return reverse('glib_sftp:sftp')

    def get_context_data(self, **kwargs):
        context = super(CreateSftp, self).get_context_data()
        context['page_type'] = "Create Sftp"
        return context


class UpdateSftp(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = SFTPConfiguration
    form_class = CreateSFTPConfigurationForm
    template_name = 'glib_sftp/sftp_create.html'

    def dispatch(self, request, *args, **kwargs):
        if AccountConfiguration.objects.first().show_sftp:
            return super(UpdateSftp, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get_success_url(self):
        return reverse('glib_sftp:sftp')

    def get_context_data(self, **kwargs):
        context = super(UpdateSftp, self).get_context_data()
        context['page_type'] = "Update Sftp"
        return context


class DeleteSftp(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = SFTPConfiguration
    template_name = 'glib_sftp/sftp_delete.html'
    group_required = ('superuser',)

    def dispatch(self, request, *args, **kwargs):
        if AccountConfiguration.objects.first().show_sftp:
            return super(DeleteSftp, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get_success_url(self):
        return reverse('glib_sftp:sftp')


class OverViewSftpEvent(LoginRequiredMixin, GroupRequiredMixin, FilterView, SingleTableView):
    model = SFTPRequest
    table_class = SftpEventTable
    template_name = 'glib_sftp/sftp_event_display.html'
    filterset_class = SftpEventFilter

    def dispatch(self, request, *args, **kwargs):
        if AccountConfiguration.objects.first().show_sftp:
            return super(OverViewSftpEvent, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied

    def get_queryset(self):
        query = super(OverViewSftpEvent, self).get_queryset()
        return query.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super(OverViewSftpEvent, self).get_context_data(**kwargs)
        f = context['filter']
        has_filter = any(
            field in self.request.GET for field in set(f.get_fields()))
        context['has_filter'] = has_filter
        context['total_events'] = SFTPRequest.objects.count()
        return context
