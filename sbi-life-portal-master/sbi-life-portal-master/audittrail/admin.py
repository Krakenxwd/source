from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from audittrail.models import UserRequestLog


# Register your models here.
class UserRequestLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'endpoint', 'exec_time', 'event_category', 'change_summary', 'created_at',)
    ordering = ('-created_at',)
    search_fields = ('email', 'event_category',)
    list_filter = (
        ('created_at', DateFieldListFilter),
    )


admin.site.register(UserRequestLog, UserRequestLogAdmin)
