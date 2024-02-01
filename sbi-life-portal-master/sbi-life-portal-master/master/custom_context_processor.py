from django.db import connection

from master.models import AccountConfiguration


def show_setting_fields(request):
    print(request)
    config = AccountConfiguration.objects.first()
    if not config:
        return {}

    context = {
        'is_sftp_configured': config.show_sftp,
    }
    return context
