import django_filters as filters
from django.contrib.auth.models import User
from django.db.models import Q


def user_search_filter(queryset, name, value):
    return queryset.filter(Q(first_name__icontains=value) | Q(email__icontains=value) |
                           Q(username__icontains=value))


def user_is_active_filter(queryset, name, value):
    value = True if value == 'yes' else False
    return queryset.filter(is_active=value)


def user_groups_filter(queryset, name, value):
    return queryset.filter(groups__id=value)


class UserFilterView(filters.FilterSet):
    search = filters.CharFilter(method=user_search_filter)
    is_active = filters.CharFilter(method=user_is_active_filter)
    groups = filters.CharFilter(method=user_groups_filter)

    class Meta:
        model = User
        fields = ['search', 'is_active', 'groups']
