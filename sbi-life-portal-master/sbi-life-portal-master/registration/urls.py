from django.urls import path, include

from registration.views import UserMaster, SetUserStatusView, SetUserGroupView, InviteUserView

app_name = 'registration'

urlpatterns = [
    path('', UserMaster.as_view(), name='users'),
    path('change/', include([
        path('status/', SetUserStatusView.as_view(), name='user.active.inactive'),
        path('group/', SetUserGroupView.as_view(), name='user.assign.group'),
    ])),
    path('invite/', InviteUserView.as_view(), name='invite')
]
