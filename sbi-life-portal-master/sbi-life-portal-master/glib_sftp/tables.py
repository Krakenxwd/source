import django_filters
import django_tables2 as tables
from django.utils.html import format_html

from glib_sftp.models import SFTPConfiguration
from glib_sftp.models import SFTPRequest


def sftp_filter(queryset, name, value):
    return queryset.filter(file_path__icontains=value)


def sftp_is_active_filter(queryset, name, value):
    value = True if value == '1' else False
    return queryset.filter(active=value)


class SFTPFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=sftp_filter)
    is_active = django_filters.CharFilter(method=sftp_is_active_filter)

    class Meta:
        model = SFTPConfiguration
        fields = ['search', 'is_active']


class SFTPConfigurationTable(tables.Table):
    action = tables.TemplateColumn(verbose_name='Action',
                                   template_name='glib_sftp/table/sftp_action.html',
                                   orderable=False)
    active = tables.TemplateColumn(verbose_name='Active', template_name='glib_sftp/table/sftp_active.html')
    url = tables.Column(verbose_name='URL', accessor='pk', attrs={
        'class': 'text-blue-500'
    })

    class Meta:
        model = SFTPConfiguration
        fields = ('pk', 'url', 'file_path', 'active', 'created_at')
        attrs = {
            "class": "w-full text-sm",
            "thead": {
                "class": "text-left"
            },
            "th": {
                "class": "px-3 py-3 bg-gray-50",
            },
            "td": {
                "class": "px-3 py-3 border-b",
                "style": "max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;",
            },
            "tbody": {
                "class": "text-gray-600"
            },
        }

        row_attrs = {
            "class": "border"
        }

    @staticmethod
    def render_url(record: SFTPConfiguration):
        return f'sftp://{record.username}:{record.password}@{record.host}'

    def before_render(self, request):
        self.columns.hide('pk')


class SftpEventTable(tables.Table):
    status = tables.Column(accessor='pk')
    file = tables.FileColumn()
    message = tables.Column()
    created_at = tables.Column()

    class Meta:
        model = SFTPRequest
        fields = ('created_at', 'file', 'pk', 'message', 'status')
        attrs = {
            "class": "w-full text-sm border",
            "thead": {
                "class": "text-left border"
            },
            "th": {
                "class": "px-3 py-3",
            },
            "td": {
                "class": "px-3 py-3 border-b",
                "style": "max-width: 300px; min-width:75px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;",
            },
            "tbody": {
                "class": "text-gray-600"
            },
        }

    @staticmethod
    def render_status(record: SFTPRequest):
        if record.status == SFTPRequest.DOWNLOADING:
            content = """<span class="py-1 text-sm px-1.5 bg-yellow-100 text-yellow-600 rounded-md capitalize">{}</span>""".format(
                'Downloading')
        elif record.status == SFTPRequest.DOWNLOADED:
            content = """<span class="py-1 text-sm px-1.5 bg-green-100 text-green-600 rounded-md capitalize">{}</span>""".format(
                'Downloaded')
        elif record.status == SFTPRequest.INITIATED:
            content = """<span class="py-1 text-sm px-1.5 bg-pink-100 text-pink-600 rounded-md capitalize">{}</span>""".format(
                'Initiated')
        elif record.status == SFTPRequest.UPLOADING:
            content = """<span class="py-1 text-sm px-1.5 bg-blue-100 text-blue-600 rounded-md capitalize">{}</span>""".format(
                'Uploading')
        elif record.status == SFTPRequest.UPLOADED:
            content = """<span class="py-1 text-sm px-1.5 bg-purple-100 text-purple-600 rounded-md capitalize">{}</span>""".format(
                'Uploaded')
        elif record.status == SFTPRequest.ERROR:
            content = """<span class="py-1 text-sm px-1.5 bg-red-100 text-red-600 rounded-md capitalize">{}</span>""".format(
                'Failed')
        elif record.status == SFTPRequest.TEST_INITIATED:
            content = """<span class="py-1 text-sm px-1.5 bg-red-100 text-red-600 rounded-md capitalize">{}</span>""".format(
                'Test Initiated')
        elif record.status == SFTPRequest.TEST_DOWNLOADING:
            content = """<span class="py-1 text-sm px-1.5 bg-red-100 text-red-600 rounded-md capitalize">{}</span>""".format(
                'Test Downloading')
        elif record.status == SFTPRequest.TEST_DOWNLOADED:
            content = """<span class="py-1 text-sm px-1.5 bg-red-100 text-red-600 rounded-md capitalize">{}</span>""".format(
                'Test Downloaded')
        elif record.status == SFTPRequest.TEST_UPLOADING:
            content = """<span class="py-1 text-sm px-1.5 bg-red-100 text-red-600 rounded-md capitalize">{}</span>""".format(
                'Test Uploading')
        elif record.status == SFTPRequest.TEST_UPLOADED:
            content = """<span class="py-1 text-sm px-1.5 bg-red-100 text-red-600 rounded-md capitalize">{}</span>""".format(
                'Test Uploaded')
        elif record.status == SFTPRequest.TEST_ERROR:
            content = """<span class="py-1 text-sm px-1.5 bg-red-100 text-red-600 rounded-md capitalize">{}</span>""".format(
                'Test Failed')
        else:
            content = """<span class="py-1 text-sm px-1.5 bg-red-100 text-red-600 rounded-md capitalize">{}</span>""".format(
                'Unknown')
        return format_html(content)
    
    @staticmethod
    def render_message(record: SFTPRequest):
        content = """<span class="" title="{}">{}</span>""".format(
                record.message, record.message)
        return format_html(content)

    def before_render(self, request):
        self.columns.hide('pk')


def sftp_event_filter(queryset, name, value):
    return queryset.filter(message__icontains=value)


def sftp_event_status_filter(queryset, name, value):
    return queryset.filter(status=value)


class SftpEventFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=sftp_event_filter)
    status = django_filters.CharFilter(method=sftp_event_status_filter)

    class Meta:
        model = SFTPRequest
        fields = ['search', 'status']
