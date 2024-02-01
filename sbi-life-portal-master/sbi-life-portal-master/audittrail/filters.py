import django_filters as filters
from django.contrib.auth.models import User
from django.db.models import Q
from audittrail.models import UserRequestLog

def userhistory_search_filter(queryset, name, value):
    return queryset.filter(Q(email__icontains=value) | Q(endpoint__icontains=value) |
                           Q(action__icontains=value))

def userhistory_request_type_filter(queryset, name, value):
    return queryset.filter(action__icontains=value)

class UserHistoryLogFilter(filters.FilterSet):
    search = filters.CharFilter(method=userhistory_search_filter)
    request_type = filters.CharFilter(method=userhistory_request_type_filter)

    class Meta:
        model = UserRequestLog
        fields = ['search', 'request_type']

