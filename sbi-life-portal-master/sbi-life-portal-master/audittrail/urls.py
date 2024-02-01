from django.urls import path
from audittrail.views import UserSiteHistoryView
app_name = 'audittrail'

urlpatterns = [
    path('<int:pk>/user/', UserSiteHistoryView.as_view(), name='user_site_history'),
]
