from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True, editable=False, null=True)
    modified_at = models.DateTimeField(
        auto_now=True, editable=False, null=True)

    class Meta:
        abstract = True


class UserMixin(models.Model):
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL,
                                   related_name="%(app_label)s_%(class)s_created_by_related",
                                   related_query_name="%(app_label)s_%(class)ss_created_by",
                                   editable=False)
    modified_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL,
                                    related_name="%(app_label)s_%(class)s_modified_by_related",
                                    related_query_name="%(app_label)s_%(class)ss_modified_by",
                                    editable=False)

    class Meta:
        abstract = True


class BoundingBoxMixin(models.Model):
    w_min = models.FloatField(default=0, blank=True, null=True)
    w_max = models.FloatField(default=0, blank=True, null=True)
    h_min = models.FloatField(default=0, blank=True, null=True)
    h_max = models.FloatField(default=0, blank=True, null=True)

    class Meta:
        abstract = True


class DataTypeMixin(models.Model):
    TEXT = 'text'
    DATE = 'date'
    AMOUNT = 'amount'
    BOOLEAN = 'boolean'
    IMAGE = 'image'

    DATA_TYPES = (
        (TEXT, 'Text'),
        (DATE, 'Date'),
        (AMOUNT, 'Amount'),
        (BOOLEAN, 'Boolean'),
        (IMAGE, 'Image'),
    )

    data_type = models.CharField(
        max_length=50, choices=DATA_TYPES, default=TEXT)

    class Meta:
        abstract = True


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.id = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class GroupMasterTypeMixin(TimestampMixin, UserMixin, models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    tag_name = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class GroupPageLabelMixin(TimestampMixin, UserMixin, models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    tag_name = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class GroupFieldMixin(TimestampMixin, UserMixin, DataTypeMixin, models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    tag_name = models.CharField(max_length=100, null=True, blank=True)
    ml_model_name = models.CharField(max_length=255, null=True, blank=True)
    do_postprocessing = models.BooleanField(default=False)
    is_multi_line = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class DocumentMixin(models.Model):
    name = models.CharField(max_length=255, verbose_name='File Name', blank=True, null=True, editable=False)
    file = models.FileField(verbose_name='File', blank=True, null=True)
    mime_type = models.CharField(
        verbose_name='Mime Type', blank=True, null=True, default='', max_length=256)
    num_pages = models.IntegerField(default=0, editable=False)

    class Meta:
        abstract = True


class PageFieldMixin(models.Model):
    text = models.CharField(max_length=1024, null=True, blank=True)
    value_text = models.CharField(max_length=1024, null=True, blank=True)
    value_date = models.DateField(null=True, blank=True)
    value_amount = models.FloatField(null=True, blank=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    value_image = models.FileField(blank=True, null=True)
    is_extracted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        abstract = True


class TrailMixin(TimestampMixin, UserMixin):
    class Meta:
        abstract = True
