import os
import uuid

import numpy as np
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from shapely.geometry import box

from master.models import ExtractionConfiguration, MasterPageLabel, MasterField, MasterType, DigitalMasterField
from mixins.models import TimestampMixin, UserMixin, DocumentMixin, BoundingBoxMixin, PageFieldMixin, BaseModel, \
    UUIDMixin, TrailMixin


# Create your models here.

class CompletedDocuments(models.Manager):
    def get_queryset(self):
        return super(CompletedDocuments, self).get_queryset().filter(status=ApplicationDocument.COMPLETED)


class QueuedDocuments(models.Manager):
    def get_queryset(self):
        return super(QueuedDocuments, self).get_queryset().filter(status=ApplicationDocument.QUEUED)


class ProcessingDocuments(models.Manager):
    def get_queryset(self):
        return super(ProcessingDocuments, self).get_queryset().filter(status=ApplicationDocument.PROCESSING)


class FailedDocuments(models.Manager):
    def get_queryset(self):
        return super(FailedDocuments, self).get_queryset().filter(status=ApplicationDocument.ERROR)


class DeletedDocuments(models.Manager):
    def get_queryset(self):
        return super(DeletedDocuments, self).get_queryset().filter(status=ApplicationDocument.DELETED)


class ApprovedDocuments(models.Manager):
    def get_queryset(self):
        return super(ApprovedDocuments, self).get_queryset().filter(validation_status=ApplicationDocument.APPROVED)


class RejectedDocuments(models.Manager):
    def get_queryset(self):
        return super(RejectedDocuments, self).get_queryset().filter(validation_status=ApplicationDocument.REJECTED)


class NeedReviewDocuments(models.Manager):
    def get_queryset(self):
        return super(NeedReviewDocuments, self).get_queryset().filter(validation_status=ApplicationDocument.NEED_REVIEW)


class ApplicationDocument(DocumentMixin, TimestampMixin, UserMixin, UUIDMixin):
    configuration = models.ForeignKey(ExtractionConfiguration, on_delete=models.CASCADE,
                                      related_name='applicatipn_documents')

    # Application Type :- KYC, Claim Form
    master_type = models.ForeignKey(MasterType, on_delete=models.SET_NULL, related_name='master_types', null=True,
                                    blank=True)
    policy_number = models.CharField(max_length=255, unique=True, null=True, blank=True)
    proposal_number = models.CharField(max_length=255, null=True, blank=True)
    date_of_intimation = models.DateField(null=True, blank=True)
    source_name = models.CharField(verbose_name='Source Name', max_length=100, null=True, blank=True)
    preprocessed_file = models.FileField(verbose_name='Pre Processed File', null=True, blank=True, editable=False)
    extracted_summary_pdf = models.FileField(verbose_name='Extracted Summary PDF', null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    is_validated = models.BooleanField(default=False)
    reason = models.TextField(null=True, blank=True)

    num_pages = models.PositiveIntegerField(editable=False, default=0)

    job_started_at = models.DateTimeField(null=True, blank=True)
    job_completed_at = models.DateTimeField(blank=True, null=True)

    hash = models.CharField(max_length=255, null=True, blank=True)
    marked_for_training = models.BooleanField(default=False)
    marked_for_reviewed = models.BooleanField(default=False)

    digital_json_data = models.JSONField(
        verbose_name='Digital Json', blank=True, null=True)
    ref_json_data = models.JSONField(
        verbose_name='Reference Json', blank=True, null=True)
    score_json_data = models.JSONField(
        verbose_name='Score Json', blank=True, null=True)
    name_to_original = models.JSONField(
        verbose_name='Name to Original', blank=True, null=True)
    field_type_matching = models.JSONField(
        verbose_name='Field Type Matching', blank=True, null=True)
    processed_digital_data = models.FileField(blank=True, null=True)
    json_response = models.FileField(
        verbose_name='Json Response', blank=True, null=True)

    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    DELETED = 'deleted'
    ERROR = 'error'

    STATUS_CHOICES = (
        (QUEUED, 'In Queue'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Success'),
        (DELETED, 'Deleted'),
        (ERROR, 'Error')
    )

    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    NEED_REVIEW = 'need_review'

    VALIDATION_STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (NEED_REVIEW, 'Need Review'),
    )

    WEB = 'web'
    API = 'api'
    ZIP = 'zip'
    SFTP = 'sftp'
    EMAIL_READER = 'email_reader'

    MODE_CHOICES = (
        (WEB, 'WEB'),
        (API, 'API'),
        (ZIP, 'ZIP'),
        (SFTP, 'SFTP'),
        (EMAIL_READER, 'Email Reader')
    )

    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=QUEUED)
    validation_status = models.CharField(
        max_length=50, choices=VALIDATION_STATUS_CHOICES, default=PENDING)

    mode = models.CharField(max_length=50, choices=MODE_CHOICES, default=WEB)

    objects = models.Manager()
    completed = CompletedDocuments()
    failed = FailedDocuments()
    deleted = DeletedDocuments()
    queued = QueuedDocuments()
    processing = ProcessingDocuments()
    approved = ApprovedDocuments()
    rejected = RejectedDocuments()
    need_review = NeedReviewDocuments()

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['configuration']),
            models.Index(fields=['preprocessed_file']),
            models.Index(fields=['job_started_at']),
            models.Index(fields=['job_completed_at']),
            models.Index(fields=['hash']),
            models.Index(fields=['created_at']),
            models.Index(fields=['modified_at']),
            models.Index(fields=['created_by']),
            models.Index(fields=['modified_by']),
        ]

    def __str__(self):
        return str(self.pk)

    def mark_as_need_review(self):
        self.validation_status = ApplicationDocument.NEED_REVIEW
        self.save()

    def mark_as_validation_approved(self):
        self.validation_status = ApplicationDocument.APPROVED
        self.save()

    def mark_as_validation_rejected(self):
        self.validation_status = ApplicationDocument.REJECTED
        self.save()

    def get_absolute_url(self):
        return reverse('claim_application:detail.summary', args=[str(self.id)])

    def log(self, code, message, level, payload, notify=False):
        ApplicationDocumentLog.objects.create(application_document=self,
                                              code=code,
                                              message=message,
                                              level=level,
                                              notify=notify,
                                              payload=payload)

    def log_task_submitted(self):
        code = ApplicationDocumentLog.APPLICATION_DOCUMENT_SUBMITTED
        message = ""
        level = ApplicationDocumentLog.L_INFO
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload)

    def log_extraction_start(self):
        code = ApplicationDocumentLog.EXTRACTION_START
        message = ""
        level = ApplicationDocumentLog.L_INFO
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload)

    def log_extraction_complete(self):
        code = ApplicationDocumentLog.EXTRACTION_COMPLETE
        message = ""
        level = ApplicationDocumentLog.L_INFO
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload)

    def log_extraction_error(self, message: str = ''):
        code = ApplicationDocumentLog.EXTRACTION_ERROR
        level = ApplicationDocumentLog.L_ERROR
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload)

    def log_processed(self):
        code = ApplicationDocumentLog.APPLICATION_DOCUMENT_PROCESSED
        message = ""
        level = ApplicationDocumentLog.L_INFO
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload, notify=True)

    def log_invalid(self, message: str = ''):
        code = ApplicationDocumentLog.APPLICATION_DOCUMENT_INVALID
        level = ApplicationDocumentLog.L_INFO
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload, notify=True)

    def log_error(self, message: str = ''):
        code = ApplicationDocumentLog.APPLICATION_DOCUMENT_ERROR
        level = ApplicationDocumentLog.L_ERROR
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload, notify=True)

    def log_sftp_received(self):
        code = ApplicationDocumentLog.DOCUMENTS_RECIEVED_FROM_SFTP
        message = ""
        level = ApplicationDocumentLog.L_INFO
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload)

    def log_sent_to_sftp(self):
        code = ApplicationDocumentLog.DOCUMENTS_SENT_TO_SFTP
        message = ""
        level = ApplicationDocumentLog.L_INFO
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload)

    def log_validations_run_start(self):
        code = ApplicationDocumentLog.VALIDATIONS_RUN_START
        message = ""
        level = ApplicationDocumentLog.L_INFO
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload)

    def log_validations_run_finish(self):
        code = ApplicationDocumentLog.VALIDATIONS_RUN_FINISH
        message = ""
        level = ApplicationDocumentLog.L_INFO
        payload = {}
        self.log(code=code, message=message, level=level, payload=payload)

    def get_nominees(self):
        return self.claimant_set.filter(type=Claimant.NOMINEE).all()

    def get_claim_form_pages(self):
        return self.pages.filter(page_labels__master_page_label__code='claim_form',
                                 page_labels__master_page_label__is_active=True)


class SingleDocument(DocumentMixin, TimestampMixin, UserMixin, BaseModel):
    RAW = "RAW"
    PROCESSED = "PROCESSED"
    CONSOLIDATED = "CONSOLIDATED"
    TYPE_CHOICE = (
        (RAW, 'RAW'),
        (PROCESSED, 'PROCESSED'),
        (CONSOLIDATED, 'CONSOLIDATED')
    )
    document = models.ForeignKey(ApplicationDocument, on_delete=models.CASCADE,
                                 related_name='single_documents')
    file_password = models.CharField(max_length=255, verbose_name='File Password', null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    type = models.CharField(choices=TYPE_CHOICE, default=RAW, max_length=20)

    class Meta:
        indexes = [
            models.Index(fields=['document']),
        ]

    def __str__(self):
        return self.name


class Claimant(UserMixin, TimestampMixin, BaseModel):
    document = models.ForeignKey(ApplicationDocument, on_delete=models.CASCADE)

    HOLDER = 'Holder'
    NOMINEE = 'Nominee'
    TYPE_CHOICES = (
        (HOLDER, 'holder'),
        (NOMINEE, 'nominee')
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=HOLDER)
    customer_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return "{}_{}".format(self.id, self.type)

    def get_pages(self):
        return self.claimant_pages.prefetch_related('page_labels').order_by('page_labels__master_page_label')


class ClaimantFields(PageFieldMixin, UserMixin, TimestampMixin, BaseModel):
    claimant = models.ForeignKey(Claimant, on_delete=models.CASCADE, related_name='claimant_fields')
    digital_master_field = models.ForeignKey(DigitalMasterField, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['claimant']),
            models.Index(fields=['digital_master_field']),
            models.Index(fields=['text']),
            models.Index(fields=['value_text']),
            models.Index(fields=['value_date']),
            models.Index(fields=['value_amount']),
            models.Index(fields=['value_boolean']),
            models.Index(fields=['is_active']),
        ]


class Page(UserMixin, TimestampMixin, BaseModel):
    document = models.ForeignKey(ApplicationDocument, on_delete=models.CASCADE, related_name='pages')
    claimant = models.ForeignKey(Claimant, on_delete=models.SET_NULL, related_name='claimant_pages', null=True,
                                 blank=True)

    number = models.PositiveIntegerField(editable=False)
    width = models.FloatField(editable=False)
    height = models.FloatField(editable=False)

    pre_processed_file = models.FileField(upload_to='pdf', null=True, blank=True)
    file = models.FileField(upload_to='pdf', null=True, blank=True)
    pre_processed_image = models.FileField(upload_to='images', null=True, blank=True)
    image = models.FileField(upload_to='images', blank=True, null=True)
    is_processed = models.BooleanField(default=False)
    is_front = models.BooleanField(blank=True, null=True)

    job_started_at = models.DateTimeField(blank=True, null=True)
    job_completed_at = models.DateTimeField(blank=True, null=True)

    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    ERROR = 'error'

    STATUS_CHOICES = (
        (QUEUED, 'In Queue'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Success'),
        (ERROR, 'Error')
    )

    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=QUEUED)

    class Meta:
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['number']),
            models.Index(fields=['width']),
            models.Index(fields=['height']),
            models.Index(fields=['is_processed']),
            models.Index(fields=['job_started_at']),
            models.Index(fields=['job_completed_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['modified_at']),
            models.Index(fields=['created_by']),
            models.Index(fields=['modified_by']),
        ]

    def get_page_label(self):
        return self.page_labels.first().master_page_label

    @staticmethod
    def sort_words(words):
        return sorted(words,
                      key=lambda x: (
                          np.floor((x['h_min'] / 2 + x['h_max'] / 2)), np.floor((x['w_min'] / 2 + x['w_max'] / 2) / 2)))

    def find_text_by_location(self, w_min, h_min, w_max, h_max):
        if (w_min == 0) and (w_max == 0) and (h_min == 0) and (h_max == 0):
            return ''
        words = self.words.all().values()
        polygons = [box(word['w_min'], word['h_min'],
                        word['w_max'], word['h_max']) for word in words]
        find_polygon = box(w_min, h_min, w_max, h_max)
        indices = [dx for dx, p in enumerate(
            polygons) if p.intersects(find_polygon)]
        areas = [
            (dx, polygons[dx].intersection(find_polygon).area /
             max(10e-9, min([polygons[dx].area, find_polygon.area])))
            for dx in indices
        ]
        areas = [x for x in areas if x[1] > 0.9]
        match_words = [words[dx] for dx, _ in areas]
        match_words = self.sort_words(match_words)
        if match_words:
            text = ' '.join([w['word'] for w in match_words])
            return text
        return ''

    def get_active_fields(self):
        return self.document.configuration.master_fields.filter(is_active=True,
                                                                page_label=self.get_page_label())


class Word(BoundingBoxMixin, BaseModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='words')
    word = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['page']),
            models.Index(fields=['word']),
        ]


class PageLabel(TimestampMixin, UserMixin, BaseModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='page_labels')
    master_page_label = models.ForeignKey(MasterPageLabel, on_delete=models.SET_NULL, null=True, blank=True)
    confidence = models.FloatField(default=0.0)

    class Meta:
        indexes = [
            models.Index(fields=['page']),
            models.Index(fields=['master_page_label']),
        ]


class PageField(PageFieldMixin, BoundingBoxMixin, TimestampMixin, UserMixin, BaseModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='pagefields')
    master_field = models.ForeignKey(MasterField, on_delete=models.CASCADE)
    original_page_number = models.PositiveIntegerField(null=True, blank=True, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=['page']),
            models.Index(fields=['master_field']),
            models.Index(fields=['text']),
            models.Index(fields=['value_text']),
            models.Index(fields=['value_date']),
            models.Index(fields=['value_amount']),
            models.Index(fields=['value_boolean']),
            models.Index(fields=['is_active']),
        ]


class FieldScore(BaseModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='field_scores')
    master_field = models.ForeignKey(MasterField, on_delete=models.CASCADE)
    score = models.FloatField(null=True, blank=True)


class ValidationConfiguration(TimestampMixin, models.Model):
    DOCUMENT = 'document'

    CONFIGURATION_CHOICES = (
        (DOCUMENT, 'Document'),
    )

    validation_name = models.CharField(max_length=50)
    configuration_for = models.CharField(
        max_length=50, choices=CONFIGURATION_CHOICES)


class ValidationRuleEngine(TimestampMixin, models.Model):
    MANDATORY = 'mandatory'
    OPTIONAL = 'optional'
    OFF = 'off'

    VALIDATION_ACTION_CHOICES = (
        (MANDATORY, 'Mandatory'),
        (OPTIONAL, 'Optional'),
        (OFF, 'Off')
    )

    validation_configuration = models.ForeignKey(ValidationConfiguration, on_delete=models.CASCADE,
                                                 related_name='validation_rule_engine')
    validation_code = models.CharField(max_length=6, null=False, blank=False)
    validation_action = models.CharField(
        max_length=50, choices=VALIDATION_ACTION_CHOICES)
    validation_description = models.CharField(
        max_length=256, null=True, blank=True)

    class Meta:
        unique_together = ('validation_configuration', 'validation_code')

    def __str__(self):
        return self.validation_code


class TemporaryValidation(TimestampMixin, BaseModel):
    SUCCESS = 'success'
    FAILED = 'failed'

    STATUS_CHOICES = (
        (SUCCESS, 'Success'),
        (FAILED, 'Failed')
    )

    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=FAILED)
    claimant = models.ForeignKey(Claimant, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='claimant_temp_validations')
    field = models.ForeignKey(MasterField, on_delete=models.CASCADE, related_name='field_temp_validations',
                              blank=True, null=True)
    page_field = models.ForeignKey(PageField, on_delete=models.CASCADE, related_name='pagefield_temp_validations',
                                   blank=True, null=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='page_temp_validations', null=True,
                             blank=True)
    reason = models.TextField(blank=True, null=True)
    rule = models.ForeignKey(ValidationRuleEngine, on_delete=models.CASCADE, blank=True,
                             null=True,
                             related_name='temporary_validation_rule')


class ReProcessDocumentEvents(TimestampMixin, UserMixin, BaseModel):
    document = models.ForeignKey(
        ApplicationDocument, on_delete=models.CASCADE, related_name='re_run_events')

    OPEN = 'open'
    CLOSE = 'close'

    RE_PROCESS_STATUS_CHOICES = (
        (OPEN, 'Open'),
        (CLOSE, 'Close'),
    )

    status = models.CharField(
        max_length=50, choices=RE_PROCESS_STATUS_CHOICES, default=CLOSE)

    class Meta:
        indexes = [
            models.Index(fields=['document'])
        ]


class DocumentReferenceTable(TimestampMixin, UserMixin, BaseModel):
    document = models.ForeignKey(
        ApplicationDocument, on_delete=models.CASCADE, related_name='doc_references')
    name = models.CharField(
        max_length=256, verbose_name='File Name', editable=False)
    num_process = models.IntegerField(default=0)
    num_pages = models.PositiveIntegerField(editable=False, default=0)

    class Meta:
        indexes = [
            models.Index(fields=['document'])
        ]


class DocumentProcessReferenceId(TimestampMixin, UserMixin, BaseModel):
    document = models.ForeignKey(
        ApplicationDocument, on_delete=models.CASCADE, related_name='document_process_reference_id')
    reference_id = models.CharField(max_length=50, null=True, blank=True)


class TempDumpFilesLog(TimestampMixin, BaseModel):
    """
    Logs and save for all the Processing Files or json
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(null=True, blank=True)
    json_response = models.JSONField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    extra_params = models.JSONField(null=True, blank=True)

    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    ERROR = 'error'

    STATUS_CHOICES = (
        (QUEUED, 'Queued'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Success'),
        (ERROR, 'Error')
    )

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=QUEUED)

    EXCEL = 'excel'
    CSV = 'csv'

    FILE_TYPE_CHOICES = (
        (EXCEL, 'Excel'),
        (CSV, 'Csv'),
    )

    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, null=True, blank=True)


class ApplicationDocumentLog(TrailMixin, models.Model):
    application_document = models.ForeignKey(ApplicationDocument, on_delete=models.CASCADE, related_name='logs')

    APPLICATION_DOCUMENT_SUBMITTED = 'APPLICATION_DOCUMENT_SUBMITTED'
    EXTRACTION_START = 'EXTRACTION_START'
    EXTRACTION_COMPLETE = 'EXTRACTION_COMPLETE'
    EXTRACTION_ERROR = 'EXTRACTION_ERROR'
    APPLICATION_DOCUMENT_PROCESSED = 'APPLICATION_DOCUMENT_PROCESSED'
    APPLICATION_DOCUMENT_INVALID = 'APPLICATION_DOCUMENT_INVALID'
    APPLICATION_DOCUMENT_ERROR = 'APPLICATION_DOCUMENT_ERROR'
    DOCUMENTS_RECIEVED_FROM_SFTP = 'DOCUMENTS_RECIEVED_FROM_SFTP'
    DOCUMENTS_SENT_TO_SFTP = 'DOCUMENTS_SENT_TO_SFTP'
    VALIDATIONS_RUN_START = 'VALIDATIONS_RUN_START'
    VALIDATIONS_RUN_FINISH = 'VALIDATIONS_RUN_FINISH'

    CODE_CHOICES = (
        (APPLICATION_DOCUMENT_SUBMITTED, 'Application Document Submitted'),
        (EXTRACTION_START, 'Extraction Start'),
        (EXTRACTION_COMPLETE, 'Extraction Complete'),
        (EXTRACTION_ERROR, 'Extraction Error'),
        (APPLICATION_DOCUMENT_PROCESSED, 'Application Document Processed'),
        (APPLICATION_DOCUMENT_INVALID, 'Application Document Invalid'),
        (APPLICATION_DOCUMENT_ERROR, 'Application Document Error'),
        (DOCUMENTS_RECIEVED_FROM_SFTP, 'Documents Recieved From SFTP'),
        (DOCUMENTS_SENT_TO_SFTP, 'Documents Sent To SFTP'),
        (VALIDATIONS_RUN_START, 'Validations Run Start'),
        (VALIDATIONS_RUN_FINISH, 'Validations Run Finish'),
    )

    code = models.CharField(max_length=50, choices=CODE_CHOICES, default=APPLICATION_DOCUMENT_SUBMITTED)
    message = models.TextField()
    L_INFO = 'INFO'
    L_ERROR = 'ERROR'
    L_WARNING = 'WARNING'
    LEVEL_CHOICES = (
        (L_INFO, 'INFO'),
        (L_ERROR, 'ERROR'),
        (L_WARNING, 'WARNING'),
    )
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default=L_INFO)
    notify = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)
    payload = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.application_document.id}/{self.level}"

    class Meta:
        ordering = ('-created_at',)


class MagicLinkHash(TimestampMixin, UserMixin, BaseModel):
    document = models.ForeignKey(ApplicationDocument, on_delete=models.CASCADE, related_name='magic_link_hashes')
    magic_hash = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_magic_link_url(self):
        if self.magic_hash:
            return reverse('claim_application:magic.detail.summary', args=[str(self.magic_hash)])
        return reverse('claim_application:magic.detail.summary', args=[str(self.id)])


class Export(TimestampMixin, UserMixin, models.Model):
    start_date = models.DateTimeField(verbose_name='Start Date')
    end_date = models.DateTimeField(verbose_name='End Date')
    file = models.FileField(
        verbose_name='Exported File', blank=True, null=True)
    csv_seperator = models.CharField(max_length=1, default=',')

    QUEUED = 'queued'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    ERROR = 'error'

    STATUS_CHOICES = (
        (QUEUED, 'In Queue'),
        (PROCESSING, 'Processing'),
        (COMPLETED, 'Success'),
        (ERROR, 'Error')
    )

    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default=QUEUED)

    EXCEL = 'excel'
    CSV = 'csv'

    FILE_TYPE_CHOICES = (
        (EXCEL, 'Excel'),
        (CSV, 'Csv'),
    )
    file_type = models.CharField(
        max_length=5, choices=FILE_TYPE_CHOICES, default=EXCEL)

    DOCUMENT = 'document'
    DIGITAL_JSON = 'digital_json'
    OUTPUT_TYPE_CHOICES = (
        (DOCUMENT, 'Document'),
        (DIGITAL_JSON, 'Digital Json'),
    )
    output_type = models.CharField(
        max_length=20, choices=OUTPUT_TYPE_CHOICES, default=DOCUMENT)
    extra_params = models.JSONField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    def filename_minus_extension(self):
        basename, extension = os.path.splitext(
            os.path.basename(self.file.name))
        return basename

    class Meta:
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]


class ExportRefName(TimestampMixin, UserMixin, models.Model):
    field_name = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=100, unique=True)
