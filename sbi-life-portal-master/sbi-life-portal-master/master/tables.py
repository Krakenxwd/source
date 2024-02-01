import django_tables2 as tables
from django.utils.html import format_html
from master.models import DigitalMasterField

class FieldScoreTable(tables.Table):
    do_scoring = tables.TemplateColumn(verbose_name='Is Active', template_name='table/field_score_active.html')
    actions = tables.TemplateColumn(verbose_name='Update Field Score', template_name='table/field_score_action.html')
    class Meta:
        model = DigitalMasterField
        fields = ('name', 'description', 'expected_score', 'do_scoring')
        attrs = {
            "class": "w-full text-sm",
            "thead": {
                "class": "text-left border"
            },
            "th": {
                "class": "px-4 py-2",
            },
            "td": {
                "class": "px-4 py-2 border-b",
            },
            "tbody": {
                "class": "text-gray-600"
            },
        }

        row_attrs = {
            "class": "border"
        }
    
    @staticmethod
    def render_name(record: DigitalMasterField):
        content = f"<span class='font-medium text-black'>{record.name}</span>"
        return format_html(content)
    
    @staticmethod
    def render_tag_name(record: DigitalMasterField):
        content = f"<span class='p-1.5 bg-gray-100 text-black rounded-md'>{record.tag_name}</span>"
        return format_html(content)
    
    @staticmethod
    def render_expected_score(record: DigitalMasterField):
        content = f"<span id='field_score_{record.id}'>{record.expected_score}</span>"
        return format_html(content)