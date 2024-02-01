from django.contrib import admin

from glib_sftp.models import SFTPConfiguration
from glib_sftp.models import SFTPFile
from glib_sftp.models import SFTPRequest
# Register your models here.

admin.site.register(SFTPConfiguration)
admin.site.register(SFTPRequest)
admin.site.register(SFTPFile)
