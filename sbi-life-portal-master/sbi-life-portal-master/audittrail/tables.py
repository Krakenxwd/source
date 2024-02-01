import django_tables2 as tables
from audittrail.models import UserRequestLog
import django_tables2 as tables

from audittrail.models import UserRequestLog


class UserSiteHistoryTable(tables.Table):
    action = tables.TemplateColumn(verbose_name='Action', template_name='table/user_action.html')
    endpoint = tables.TemplateColumn(verbose_name='Endpoint', template_name='table/user_endpoint.html')

    class Meta:
        model = UserRequestLog
        fields = ('email', 'event_category', 'endpoint', 'login_IP', 'action', 'created_at')
        attrs = {
            "class": "w-full text-sm",
            "thead": {
                "class": "text-left"
            },
            "th": {
                "class": "px-3 py-3",
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
