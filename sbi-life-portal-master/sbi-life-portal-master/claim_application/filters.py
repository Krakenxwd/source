from datetime import datetime, timedelta
from datetime import time
import re

import django_filters
from django.db.models import Q

from claim_application.models import ApplicationDocument


def list_document_search_filter(queryset, name, value):
    return queryset.filter(
        Q(id__icontains=value) | Q(hash__icontains=value) | Q(created_by__email__icontains=value) | Q(
            master_type__name__icontains=value) | Q(policy_number__icontains=value))

def list_document_by_policy_number_filter(queryset, name, value):
    return queryset.filter(
        Q(policy_number__icontains=value))

def list_document_by_claimant_id_filter(queryset, name, value):
    return queryset.filter(
        Q(claimant__customer_id__icontains=value))


def list_document_start_date_filter(queryset, name, value):
    start_date = value.split(' - ')[0]
    end_date = value.split(' - ')[1]
    start_datetime_object = datetime.strptime(
            start_date, '%d/%m/%Y %I:%M:%S %p')
    end_datetime_object = datetime.strptime(
        end_date, '%d/%m/%Y %I:%M:%S %p')
    return queryset.filter(created_at__range=(start_datetime_object, end_datetime_object))

def list_export_search_filter(queryset, name, value):
    return queryset.filter(
        Q(id__icontains=value) | Q(output_type__icontains=value) | Q(file_type__icontains=value) | Q(created_by__email__icontains=value))

def export_start_date_end_date_filter(queryset, name, value):
    if is_valid_date_range(value):
        start_date = value.split(' - ')[0]
        end_date = value.split(' - ')[1]
        start_datetime_object = datetime.strptime(
            start_date, '%d/%m/%Y %I:%M:%S %p')
        end_datetime_object = datetime.strptime(
            end_date, '%d/%m/%Y %I:%M:%S %p')
        return queryset.filter(created_at__range=(start_datetime_object, end_datetime_object))
    return queryset

def export_file_type_filter(queryset, name, value):
    return queryset.filter(file_type__icontains=value)


def export_output_type_filter(queryset, name, value):
    return queryset.filter(output_type__icontains=value)

date_range_regex = re.compile(
    r'^(0[1-9]|[1-2]\d|3[0-1])/(0[1-9]|1[0-2])/(\d{4}) (0[1-9]|1[0-2]):([0-5][0-9]):([0-5][0-9]) (am|pm) - (0[1-9]|[1-2]\d|3[0-1])/(0[1-9]|1[0-2])/(\d{4}) (0[1-9]|1[0-2]):([0-5][0-9]):([0-5][0-9]) (am|pm)$')


def is_valid_date_range(date_range_string):
    match = date_range_regex.match(date_range_string)
    if not match:
        return False
    start_month = int(match.group(2))
    end_month = int(match.group(9))
    if start_month > 12 or end_month > 12:
        return False
    return True



class ListDocumentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=list_document_search_filter)
    date_range = django_filters.CharFilter(method=list_document_start_date_filter)
    policy_no= django_filters.CharFilter(method=list_document_by_policy_number_filter)
    claim_id = django_filters.CharFilter(method=list_document_by_claimant_id_filter)
    class Meta:
        model = ApplicationDocument
        fields = ['date_range', 'mode', 'status', 'search', 'policy_no', 'claim_id']

class ExportDocumentFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=list_export_search_filter)
    date_range = django_filters.CharFilter(method=export_start_date_end_date_filter)
    export_file_type = django_filters.CharFilter(method=export_file_type_filter)
    export_output_type = django_filters.CharFilter(method=export_output_type_filter)
    class Meta:
        model = ApplicationDocument
        fields = ['date_range', 'export_file_type', 'export_output_type', 'status', 'search']