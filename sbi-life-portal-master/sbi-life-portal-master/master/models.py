from django.db import models

from mixins.models import SingletonModel, GroupPageLabelMixin, \
    GroupFieldMixin, BaseModel, GroupMasterTypeMixin, TimestampMixin


# Create your models here.
class AccountConfiguration(SingletonModel, BaseModel):
    big_logo = models.ImageField(upload_to='big_logo', blank=True, null=True)
    small_logo = models.ImageField(
        upload_to='small_logo', blank=True, null=True)
    header_text = models.CharField(max_length=255, blank=True, null=True)
    validation_based_view = models.BooleanField(default=False)
    process_based_view = models.BooleanField(default=False)
    auto_assign_worker = models.BooleanField(default=False)
    has_upload_limit = models.BooleanField(default=False)
    upload_limit = models.IntegerField(default=100)
    api_csv_separator = models.CharField(max_length=5, null=True, blank=True)
    saml_sso_config = models.JSONField(null=True, blank=True)
    show_sftp = models.BooleanField(default=False)
    max_threshold = models.FloatField(default=0)
    secret_key = models.CharField(max_length=255, default='')
    salt_value = models.CharField(max_length=255, default='')


class ExtractionConfiguration(SingletonModel, BaseModel):
    process_url = models.URLField(blank=True, null=True)
    page_classification_url = models.URLField(blank=True, null=True)
    extra_params = models.JSONField(null=True, blank=True)


class MasterType(GroupMasterTypeMixin, BaseModel):
    configuration = models.ForeignKey(ExtractionConfiguration, on_delete=models.CASCADE,
                                      related_name='application_types')

    class Meta:
        indexes = (
            models.Index(fields=['name'], name='%(class)s_name_index'),
            models.Index(fields=['code'], name='%(class)s_code_index'),
            models.Index(fields=['tag_name'], name='%(class)s_tag_name_index'),
            models.Index(fields=['is_active'], name='%(class)s_is_active_index'),
        )

    def __str__(self):
        return self.name


class MasterPageLabel(GroupPageLabelMixin, BaseModel):
    configuration = models.ForeignKey(ExtractionConfiguration, on_delete=models.CASCADE,
                                      related_name='master_page_labels')
    type = models.ForeignKey(MasterType, on_delete=models.CASCADE, null=True, blank=True)
    default = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['configuration']),
            models.Index(fields=['code']),
            models.Index(fields=['tag_name']),
        ]

    def __str__(self):
        return self.name


class MasterField(GroupFieldMixin, BaseModel):
    configuration = models.ForeignKey(ExtractionConfiguration, on_delete=models.CASCADE,
                                      related_name='master_fields')
    page_label = models.ForeignKey(MasterPageLabel, on_delete=models.CASCADE)
    do_scoring = models.BooleanField(default=False)
    output_max_length = models.IntegerField(null=True, blank=True)
    output_decimals_digit = models.IntegerField(null=True, blank=True)
    output_date_formate = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        order_with_respect_to = 'configuration'
        indexes = [
            models.Index(fields=['configuration']),
            models.Index(fields=['page_label']),
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['tag_name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.page_label.code + '-' + self.name


class DigitalMasterField(GroupFieldMixin, BaseModel):
    configuration = models.ForeignKey(ExtractionConfiguration, on_delete=models.CASCADE,
                                      related_name='digital_master_fields')
    field_type_name = models.CharField(max_length=100, null=True, blank=True)
    header = models.CharField(max_length=100)
    output_max_length = models.IntegerField(null=True, blank=True)
    output_decimals_digit = models.IntegerField(null=True, blank=True)
    output_date_formate = models.CharField(max_length=10, null=True, blank=True)

    description = models.CharField(
        max_length=256, null=True, blank=True, verbose_name='Scoring Description')
    weightage = models.FloatField(null=True, blank=True)
    allow_weightage = models.BooleanField(default=False)
    expected_score = models.FloatField(null=True, blank=True)
    do_scoring = models.BooleanField(default=False)
    show_annotation = models.BooleanField(default=False)

    class Meta:
        order_with_respect_to = 'configuration'
        indexes = [
            models.Index(fields=['configuration']),
            models.Index(fields=['name']),
            models.Index(fields=['code']),
            models.Index(fields=['tag_name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name