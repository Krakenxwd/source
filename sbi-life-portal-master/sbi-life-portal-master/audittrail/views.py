from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from audittrail.filters import UserHistoryLogFilter
from audittrail.models import UserRequestLog
from audittrail.tables import UserSiteHistoryTable
from mixins.models import User
from mixins.views import GroupRequiredMixin


# Create your views here.
class UserSiteHistoryView(LoginRequiredMixin, GroupRequiredMixin, FilterView, SingleTableView):
    model = UserRequestLog
    table_class = UserSiteHistoryTable
    template_name = 'user_site_history.html'
    group_required = ('admin',)
    filterset_class = UserHistoryLogFilter

    def get_queryset(self):
        query = super(UserSiteHistoryView, self).get_queryset()
        query = query.filter(user=self.kwargs.get('pk')).order_by('-created_at')
        return query

    def get_table(self, **kwargs):
        table = super(UserSiteHistoryView, self).get_table(**kwargs)
        if not self.request.user.is_superuser:
            table.exclude = ('login_IP',)
        return table

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        f = context['filter']
        has_filter = any(
            field in self.request.GET for field in set(f.get_fields()))
        context['has_filter'] = has_filter
        context['total_entries'] = UserRequestLog.objects.filter(user=self.kwargs.get('pk')).count()
        context['user_email'] = User.objects.get(pk=self.kwargs.get('pk')).email
        context['user_id'] = self.kwargs.get('pk')
        return context
