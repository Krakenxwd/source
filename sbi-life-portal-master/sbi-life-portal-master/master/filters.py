import django_filters as filters
from django.db.models import Q
from master.models import DigitalMasterField

def field_is_active_filter(queryset, name, value):
    value = True if value == '1' else False
    return queryset.filter(do_scoring=value)

def field_search_filter(queryset, name, value):
    return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))

class FieldScoreFilterView(filters.FilterSet):
    is_active = filters.CharFilter(method=field_is_active_filter)
    search = filters.CharFilter(method=field_search_filter)

    class Meta:
        model = DigitalMasterField
        fields = ['search', 'is_active']