from django.urls import path, include

from master.views import RunManagementCommandView, EncDecryptView, GetEncDecrAjaxView

app_name = 'master'

urlpatterns = [
    path('run/management/', RunManagementCommandView.as_view(), name='run.management'),
    path('encdcrypt/', EncDecryptView.as_view(), name='enc.decrypt'),
    path('ajax/encdryp/', GetEncDecrAjaxView.as_view(), name='ajax.enc.decrypt'),
]
