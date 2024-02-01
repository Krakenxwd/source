from django.contrib.auth.models import User
from django.db import models

from mixins.models import BaseModel, TimestampMixin


# Create your models here.
class UserRequestLog(TimestampMixin, BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField("email address", blank=True)

    # detail of client operating system
    user_agent_info = models.CharField(max_length=255, null=True, blank=True)

    # current url
    endpoint = models.CharField(max_length=255, null=True, blank=True)

    # current model
    changed_object = models.CharField(max_length=100, null=True, blank=True)

    # view name
    event_category = models.CharField(max_length=100, null=True, blank=True)
    login_IP = models.CharField(max_length=100, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    # method : GET, POST
    action = models.CharField(max_length=100, null=True, blank=True)

    change_summary = models.TextField(null=True, blank=True)
    detail = models.TextField(null=True, blank=True)

    # Time taken to create the response
    exec_time = models.FloatField(null=True)
