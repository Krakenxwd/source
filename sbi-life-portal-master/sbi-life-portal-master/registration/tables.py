import django_tables2 as tables
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import format_html


class UserTableView(tables.Table):
    is_active = tables.Column(verbose_name='Active/Inactive')
    actions = tables.TemplateColumn(verbose_name='Actions', template_name='registration/table/user_action.html')
    username = tables.Column(verbose_name='Name')

    class Meta:
        model = User
        fields = ('username', 'groups', 'email', 'date_joined', 'is_active', 'actions')
        attrs = {
            "class": "w-full border",
            "thead": {
                "class": "text-left border"
            },
            "th": {
                "class": "p-3 bg-gray-50",
            },
            "td": {
                "class": "p-3",
            },
            "tbody": {
                "class": "text-gray-600"
            },
        }

        row_attrs = {
            "class": "border-b font-normal"
        }

    def render_groups(self, record):
        content =  ' '.join([f'<span class="bg-blue-100 text-blue-600 px-2 py-1 rounded capitalize">{group.name}</span>' for group in record.groups.all()])
        return format_html(content)
    
    def render_username(self, record):
        content = """<span class="flex items-center gap-2">
                                    <span>
                                        <img src="/static/images/user.png" alt="" class="w-8 h-8">
                                    </span>
                                    <span>{}</span>
                    </span>""".format(record.username)
        return format_html(content)


    def render_is_active(self, record):
        context = {
            'is_same_group': check_if_same_group(self.request,record),
            'is_disabled': (self.request.user == record) or (not self.request.user.is_superuser and record.is_superuser) or (record.is_superuser and self.request.user.is_superuser),
            'record': record, 'request': self.request
        }
        content = render_to_string('registration/table/user_is_active.html',
                         context)
        return content

def check_if_same_group(request, record):
    for group in record.groups.all():
        if group in request.user.groups.all():
            return True
    return False