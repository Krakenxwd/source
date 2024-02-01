import binascii
import os

import pandas as pd
from allauth.account.views import PasswordResetView, PasswordResetDoneView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView
from django_filters.views import FilterView
from django_tables2 import SingleTableView

from claim_application.utils import change_timezone_for_dataframe, excel_response
from mixins.views import GroupRequiredMixin
from registration.filters import UserFilterView
from registration.tables import UserTableView
from registration.utils import send_invite_email_with_password, is_valid_email


# Create your views here.

class CustomPasswordResetView(PasswordResetView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            url = reverse('account_set_password')
            return HttpResponseRedirect(url)
        return super(CustomPasswordResetView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        redirect_url = super(CustomPasswordResetView, self).form_valid(form)
        self.request.session['password_reset_email'] = self.request.POST.get('email')
        self.request.session.modified = True
        return redirect_url


class CustomPasswordResetDoneView(PasswordResetDoneView):
    def get_context_data(self, **kwargs):
        context = super(CustomPasswordResetDoneView, self).get_context_data(**kwargs)
        context['email'] = self.request.session.get('password_reset_email', '')
        return context


class UserMaster(LoginRequiredMixin, GroupRequiredMixin, FilterView, SingleTableView):
    model = User
    table_class = UserTableView
    filterset_class = UserFilterView
    template_name = 'registration/user_master.html'
    group_required = ('admin',)

    def get_queryset(self):
        queryset = super(UserMaster, self).get_queryset()
        return queryset.order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super(UserMaster, self).get_context_data(**kwargs)
        context['is_users_data_available'] = self.get_queryset().exists()
        context['users'] = self.get_queryset()
        context['groups'] = Group.objects.all()
        context['has_filter'] = any(value for value in self.request.GET.values() if value)
        return context

        # Download a invited members.

    def post(self, request):
        users_list = []
        for user in User.objects.prefetch_related('groups').order_by('date_joined'):
            user_dict = {}
            groups = ', '.join(group.name for group in user.groups.all())
            user_dict['Name'] = user.username
            user_dict['Groups'] = groups
            user_dict['Email Address'] = user.email
            user_dict['created_at'] = user.date_joined
            user_dict['Active/Inactive'] = user.is_active
            users_list.append(user_dict)
        df = pd.DataFrame.from_records(users_list)
        change_timezone_for_dataframe(df)  # change datetime as compatible to excel report
        df.rename(columns={'created_at': 'Date Joined'}, inplace=True)
        return excel_response(df, 'Users Details')


class SetUserStatusView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ('admin',)

    def get(self, request, *args, **kwargs):
        try:
            data = {}
            code = 1
            msg = ''
            user_id = request.GET.get('user_id')
            is_active = True if request.GET.get('is_active') == 'true' else False
            if request.user.is_superuser:
                user = User.objects.filter(id=user_id)
                if user.exists() and request.user != user.first():
                    user.update(is_active=is_active)
                    msg = 'User status updated successfully.'
                    code = 1
                else:
                    msg = 'User does not exists or you cannot change your status.'
                    code = -1
            else:
                user = User.objects.filter(id=user_id)
                if user.exists() and request.user != user.first():
                    if user.first().is_superuser:
                        msg = 'Cannot update the status of this user.'
                        code = -1
                    else:
                        user.update(is_active=is_active)
                        msg = 'User status updated successfully.'
                        code = 1
                else:
                    msg = 'User does not exists or you cannot change your status.'
                    code = -1

            data['code'] = code
            data['msg'] = msg
        except Exception as e:
            data = {
                'code': -1,
                'msg': str(e)
            }
            print("Error: ", str(e))
        return JsonResponse(data)


class SetUserGroupView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ('admin',)

    def post(self, request, *args, **kwargs):
        data = dict(request.POST)
        group_id_list = data.get('group_name', '')
        target_user_id_list = data.get('user-id', '')
        if group_id_list and target_user_id_list:
            user = User.objects.filter(id=target_user_id_list[0])
            if user.exists():
                user = user.first()
                user.groups.clear()
                for group_id in group_id_list:
                    group = Group.objects.filter(id=group_id)
                    if group.exists():
                        user.groups.add(group.first())
                        messages.success(request, 'Group added successfuly.')
                    else:
                        messages.warning(request, 'Groups does not exists.')
            else:
                messages.warning(request, 'User does not exists.')
        else:
            messages.warning(request, 'Please select a group.')

        return redirect(reverse('registration:users'))


class InviteUserView(LoginRequiredMixin, GroupRequiredMixin, View):
    group_required = ('admin',)

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user = User.objects.filter(email=email).first()
        checkbox = request.POST.get('checkbox', '')
        send_copy = checkbox == 'on' if checkbox else False

        if first_name and last_name:
            if email and is_valid_email(email):
                if not user:
                    password = binascii.hexlify(os.urandom(20)).decode()
                    user = User.objects.create_user(email, email, password, first_name=first_name, last_name=last_name)
                    user.save()

                    # todo : change it to member
                    admin = Group.objects.get(name='admin')
                    user.groups.add(admin)

                    send_invite_email_with_password(email, password, send_copy=send_copy)
                    messages.success(request, "User invited successfuly.")
                else:
                    if user.last_login is None:
                        password = binascii.hexlify(os.urandom(20)).decode()
                        user.set_password(password)
                        user.save()

                        # todo : change it to member
                        admin = Group.objects.get(name='admin')
                        user.groups.add(admin)

                        send_invite_email_with_password(
                            email, password, send_copy=True)
                        messages.success(request, 'Invitation resent successfuly')
                    else:
                        messages.warning(request, 'User has already logged in.')
            else:
                messages.warning(request, 'Please enter a valid email address.')
        else:
            messages.warning(request, 'First name and last name cannot be empty.')
        return redirect(reverse('registration:users'))
