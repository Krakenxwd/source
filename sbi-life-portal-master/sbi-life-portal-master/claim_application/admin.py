from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from claim_application.models import ApplicationDocument, SingleDocument, ReProcessDocumentEvents, TempDumpFilesLog, \
    PageLabel, PageField, Page, ApplicationDocumentLog, Claimant, ClaimantFields, TemporaryValidation, FieldScore, \
    ValidationConfiguration, ValidationRuleEngine, MagicLinkHash, Export, DocumentProcessReferenceId


# Register your models here.
class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'is_processed', 'is_validated', 'marked_for_training', 'marked_for_reviewed', 'status',
        'validation_status', 'hash', 'mode')
    search_fields = ('name', 'id', 'policy_number')


class ApplicationDocumentLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'application_document', 'code', 'level', 'created_at',
    )
    search_fields = ('application_document__id',)


class SingleDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_document', 'name', 'file', 'mime_type', 'num_pages', 'type')

    def get_document(self, obj: SingleDocument):
        doc_id = obj.document.id
        return format_html(
            """<a href="{}">{}</a>""".format(
                reverse('admin:claim_application_applicationdocument_change', args={doc_id}), doc_id))

    get_document.short_description = "Application Document"


class ReProcessDocumentEventsAdmin(admin.ModelAdmin):
    list_display = ('id', 'document_id', 'status', 'created_at', 'modified_at')
    search_fields = ('document__name', 'status',)
    list_filter = ('status', 'created_at', 'modified_at')


class TempDumpFilesLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'status')
    ordering = ('-created_at',)


class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_document', 'is_processed',
                    'status')
    search_fields = ('document__name',)

    def get_document(self, obj):
        if obj.document:
            return format_html(
                """<a href="{}">{}</a>""".format(
                    reverse('admin:claim_application_applicationdocument_change', args={obj.document.id}),
                    obj.document.id))

    get_document.short_description = "Document"


class PageLabelAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_page', 'master_page_label', 'confidence')
    search_fields = ('page__id',)

    def get_page(self, obj):
        if obj.page:
            page_id = obj.page.id
            return format_html(
                """<a href="{}">{}</a>""".format(
                    reverse('admin:claim_application_page_change', args={page_id}), page_id))

    get_page.short_description = "Page"


class PageFieldAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_page', 'master_field', 'is_active', 'value_boolean',
                    'is_extracted', 'text', 'value_text',
                    'value_date', 'value_amount')
    search_fields = ('text', 'value_text', 'value_date',
                     'value_amount', 'reason')

    def get_page(self, obj):
        if obj.page:
            page_id = obj.page.id
            return format_html(
                """<a href="{}">{}</a>""".format(
                    reverse('admin:claim_application_page_change', args={page_id}), page_id))

    get_page.short_description = "Page"


class ClaimantAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'customer_id', 'type',)


class ClaimantFieldsAdmin(admin.ModelAdmin):
    list_display = ('id', 'claimant', 'text', 'digital_master_field',)


class TemporaryValidationAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'page_field', 'page', 'reason', 'rule')


class FieldScoreAdmin(admin.ModelAdmin):
    list_display = ('page', 'master_field', 'score',)


class ValidationConfigurationAdmin(admin.ModelAdmin):
    list_display = ('validation_name', 'configuration_for',)


class ValidationRuleEngineAdmin(admin.ModelAdmin):
    list_display = ('validation_configuration', 'validation_code', 'validation_action', 'validation_description')


class MagicLinkHashAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'magic_hash', 'user')


class ExportAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'status', 'output_type', 'file_type',)
    search_fields = ('file',)

class DocumentProcessReferenceIdAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'reference_id', 'created_at')
    search_fields = ('document__id', 'reference_id',)


admin.site.register(ApplicationDocument, ApplicationDocumentAdmin)
admin.site.register(SingleDocument, SingleDocumentAdmin)
admin.site.register(ReProcessDocumentEvents, ReProcessDocumentEventsAdmin)
admin.site.register(TempDumpFilesLog, TempDumpFilesLogAdmin)
admin.site.register(PageField, PageFieldAdmin)
admin.site.register(PageLabel, PageLabelAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(ApplicationDocumentLog, ApplicationDocumentLogAdmin)
admin.site.register(Claimant, ClaimantAdmin)
admin.site.register(ClaimantFields, ClaimantFieldsAdmin)
admin.site.register(ValidationConfiguration, ValidationConfigurationAdmin)
admin.site.register(ValidationRuleEngine, ValidationRuleEngineAdmin)
admin.site.register(TemporaryValidation, TemporaryValidationAdmin)
admin.site.register(FieldScore, FieldScoreAdmin)
admin.site.register(MagicLinkHash, MagicLinkHashAdmin)
admin.site.register(Export, ExportAdmin)
admin.site.register(DocumentProcessReferenceId, DocumentProcessReferenceIdAdmin)
