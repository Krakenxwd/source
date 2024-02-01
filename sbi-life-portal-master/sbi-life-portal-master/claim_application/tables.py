import django_tables2 as tables
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from claim_application.models import ApplicationDocument, SingleDocument, Export


class ListDocumentTable(tables.Table):
    checkbox = tables.TemplateColumn(verbose_name=mark_safe("<span class='p-2'><input type='checkbox' class='check-all'></span>"), template_name='claim_application/table/document_checkbox.html', orderable=False)
    id = tables.TemplateColumn(verbose_name='Document ID', template_name='claim_application/table/document_link.html')
    action = tables.TemplateColumn(verbose_name='Actions', template_name='claim_application/table/document_action.html')
    mode = tables.TemplateColumn(verbose_name='Mode', template_name='claim_application/table/document_mode.html')
    policy_number = tables.Column(verbose_name='Policy No.')
    status = tables.TemplateColumn(verbose_name='Status', template_name='claim_application/table/document_status.html')
    marked_for_reviewed = tables.TemplateColumn(verbose_name='Reviewed',
                                                template_name='claim_application/table/document_marked_for_reviewed.html')

    class Meta:
        model = ApplicationDocument
        fields = ('checkbox', 'id', 'created_at', 'policy_number', 'created_by', 'mode', 'status', 'marked_for_reviewed', 'action')
        attrs = {
            "class": "w-full text-sm",
            "thead": {
                "class": "text-left border"
            },
            "th": {
                "class": "px-3 py-3 bg-gray-50",
            },
            "td": {
                "class": "px-3 py-3 border-b",
            },
            "tbody": {
                "class": "text-gray-600"
            },
        }

        row_attrs = {
            "class": "border"
        }


class SingleDocumentTable(tables.Table):
    name = tables.TemplateColumn(verbose_name='Name', template_name='claim_application/table/view_file_name.html')
    view_file = tables.Column(verbose_name='View file', accessor='pk')

    class Meta:
        model = SingleDocument
        fields = ('name', 'num_pages', 'size', 'view_file')
        attrs = {
            "class": "w-full text-sm",
            "thead": {
                "class": "text-left border"
            },
            "th": {
                "class": "p-3",
            },
            "td": {
                "class": "px-3 py-3 border-b",
            },
            "tbody": {
                "class": "text-gray-600"
            },
        }

        row_attrs = {
            "class": "border"
        }

    @staticmethod
    def render_is_processed(record: SingleDocument):
        if record.is_processed:
            content = """<span class="p-1 bg-green-50 text-green-500 rounded-md">Yes</span>"""
        else:
            content = """<span class="p-1 bg-red-50 text-red-500 rounded-md">No</span>"""
        return format_html(content)

    def render_view_file(self, record):
        content = """<a href="{}" target="_blank" class="capitalize text-sm py-1.5 px-2 border border-blue-500 text-blue-500 rounded-md hover:text-white hover:bg-blue-500">view file</a>""".format(
            record.file.url)
        return format_html(content)


class ExportTable(tables.Table):
    id = tables.Column(verbose_name='ID')
    output_type = tables.TemplateColumn(verbose_name='Output Type', template_name='claim_application/table/export/export_output_type.html')
    status = tables.TemplateColumn(verbose_name='Status', template_name='claim_application/table/export/export_status.html')
    action = tables.TemplateColumn(verbose_name='Actions', template_name='claim_application/table/export/export_action.html')
    file_type = tables.TemplateColumn(verbose_name='File Type', template_name='claim_application/table/export/export_file_type.html')
    created_by = tables.TemplateColumn(verbose_name='Requested By', template_name='claim_application/table/export/export_user.html')
    created_at = tables.Column(verbose_name='Requested At')
    class Meta:
        model = Export
        fields = ('id', 'start_date', 'end_date', 'created_by', 'created_at', 'status', 'file_type', 'output_type', 'action')
        attrs = {
            "class": "w-full text-sm",
            "thead": {
                "class": "text-left border"
            },
            "th": {
                "class": "p-3 bg-gray-50",
            },
            "td": {
                "class": "px-3 py-3 border-b",
            },
            "tbody": {
                "class": "text-gray-600"
            },
        }

        row_attrs = {
            "class": "border"
        }