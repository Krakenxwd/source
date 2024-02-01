import django_filters


def sftp_event_filter(queryset, name, value):
    return queryset.filter(error_message__icontains=value)


def sftp_event_status_filter(queryset, name, value):
    return queryset.filter(status=value)


class SftpEventFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method=sftp_event_filter)
    status = django_filters.CharFilter(method=sftp_event_status_filter)

    class Meta:
        model = SFTPRequest
        fields = ['search', 'status']
