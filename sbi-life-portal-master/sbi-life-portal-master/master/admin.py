from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from master.models import AccountConfiguration, DigitalMasterField
from master.models import ExtractionConfiguration
from master.models import MasterField
from master.models import MasterPageLabel
from master.models import MasterType


# Register your models here.
class MasterTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)


class MasterPageLabelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'tag_name',
                    'is_active', 'get_configuration', 'default')
    search_fields = ('name', 'code', 'tag_name',)

    def get_configuration(self, obj):
        if obj.configuration:
            return format_html(
                """<a href="{}">{}</a>""".format(
                    reverse('admin:master_extractionconfiguration_change',
                            args={obj.configuration.id}),
                    obj.configuration.id))

    get_configuration.short_description = "Extraction Configuration"


class MasterFieldGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'get_configuration', 'page_label')
    search_fields = ('name', 'code')

    def get_configuration(self, obj):
        if obj.configuration:
            return format_html(
                """<a href="{}">{}</a>""".format(
                    reverse('admin:master_extractionconfiguration_change',
                            args={obj.configuration.id}),
                    obj.configuration.id))

    get_configuration.short_description = "Extraction Configuration"


class MasterFieldAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'code', 'tag_name', 'data_type', 'ml_model_name', 'page_label', 'do_scoring',
        'do_postprocessing', 'is_active',
        'get_configuration',)
    search_fields = ('name', 'code', 'tag_name', 'ml_model_name')

    def get_configuration(self, obj):
        if obj.configuration:
            return format_html(
                """<a href="{}">{}</a>""".format(
                    reverse('admin:master_extractionconfiguration_change',
                            args={obj.configuration.id}),
                    obj.configuration.id))

    get_configuration.short_description = "Extraction Configuration"


class AccountConfigurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'big_logo', 'small_logo', 'header_text', 'max_threshold')
    search_fields = ('header_text',)


class ExtractionConfigurationAdmin(admin.ModelAdmin):
    list_display = ('id', 'process_url', 'page_classification_url',)
    search_fields = ('process_url',)


class DigitalMasterFieldAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'code', 'tag_name', 'field_type_name', 'header', 'data_type', 'weightage', 'expected_score',
        'do_scoring', 'allow_weightage', 'is_active', 'description')
    search_fields = ('name', 'code', 'tag_name')


class SetFieldScorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'tag_name', 'description', 'weightage', 'expected_score', 'is_active')


admin.site.register(MasterPageLabel, MasterPageLabelAdmin)
admin.site.register(MasterField, MasterFieldAdmin)
admin.site.register(AccountConfiguration, AccountConfigurationAdmin)
admin.site.register(ExtractionConfiguration, ExtractionConfigurationAdmin)
admin.site.register(MasterType, MasterTypeAdmin)
admin.site.register(DigitalMasterField, DigitalMasterFieldAdmin)
