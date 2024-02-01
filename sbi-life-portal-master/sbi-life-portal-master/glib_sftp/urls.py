from django.urls import path

from glib_sftp.views import CreateSftp
from glib_sftp.views import DeleteSftp
from glib_sftp.views import OverViewSftp
from glib_sftp.views import OverViewSftpEvent
from glib_sftp.views import UpdateSftp

app_name = 'glib_sftp'

urlpatterns = [
    path('', OverViewSftp.as_view(), name='sftp'),
    path('create/', CreateSftp.as_view(), name='sftp_create'),
    path('<uuid:pk>/update/', UpdateSftp.as_view(), name='sftp_update'),
    path('<uuid:pk>/delete/', DeleteSftp.as_view(), name='sftp_delete'),
    path('event/', OverViewSftpEvent.as_view(), name='sftp.event'),
]
