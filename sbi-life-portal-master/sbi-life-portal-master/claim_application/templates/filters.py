from datetime import datetime, timedelta
from datetime import time

import django_filters
from django.db.models import Q

from claim_application.models import ApplicationDocument


def list_document_search_filter(queryset, name, value):
    return queryset.filter(
        Q(id__icontains=value) | Q(hash__icontains=value) | Q(created_by__email__icontains=value) | Q(
            master_type__name__icontains=value))


def list_document_start_date_filter(queryset, name, value):
    start_datetime = datetime.combine(datetime.strptime(value, '%d/%m/%y %I:%M %p'), time.min)
    return queryset.filter(created_at__gte=start_datetime)


def list_document_end_date_filter(queryset, name, value):
    end_datetime = datetime.combine(datetime.strptime(value, '%d/%m/%y %I:%M %p'), time.max)
    return queryset.filter(created_at__lte=end_datetime)


def list_document_period_filter(queryset, name, value):
    end_datetime = datetime.combine(datetime.now(), time.max)
    if value == 'today':
        start_datetime = datetime.combine(datetime.now(), time.min)
    elif value == 'yesterday':
        start_datetime = datetime.combine(datetime.now() - timedelta(days=1), time.min)
        end_datetime = datetime.combine(datetime.now() - timedelta(days=1), time.max)
    elif value == 'last_7_days':
        start_datetime = datetime.combine(datetime.now() - timedelta(days=7), time.min)
    elif value == 'last_30_days':
        start_datetime = datetime.combine(datetime.now() - timedelta(days=30), time.min)
    else:
        start_datetime = datetime(datetime.now().year, 1, 1)
    return queryset.filter(created_at__range=[start_datetime, end_datetime])


class ListDocumentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=list_document_search_filter)
    start_date = django_filters.CharFilter(method=list_document_start_date_filter)
    end_date = django_filters.CharFilter(method=list_document_end_date_filter)
    period = django_filters.CharFilter(method=list_document_period_filter)

    class Meta:
        model = ApplicationDocument
        fields = ['search', 'start_date', 'end_date', 'mode', 'status', 'period']
