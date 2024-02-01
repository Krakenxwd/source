"""sbilife URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from registration.views import CustomPasswordResetView, CustomPasswordResetDoneView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/password/reset/', CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('accounts/password/reset/done/', CustomPasswordResetDoneView.as_view(), name='account_reset_password_done'),
    path('accounts/', include('allauth.urls')),
    path('', include('claim_application.urls'), name='application'),
    path('master/', include('master.urls'), name='master'),
    path('registration/users/', include('registration.urls'), name='registration'),
    path('sftp/', include('glib_sftp.urls'), name='sftp'),
    path('audittrail/', include('audittrail.urls'), name='audittrail'),
]

if settings.MEDIA_STORAGE == 'LOCAL':
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]