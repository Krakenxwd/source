from django.contrib import admin

from registration.models import Client


# Register your models here.
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')


admin.site.register(Client, ClientAdmin)