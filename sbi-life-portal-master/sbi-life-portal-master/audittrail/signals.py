import traceback

import django.dispatch
from django.dispatch import receiver, Signal

from audittrail.models import UserRequestLog
import logging
import datetime


# creates a custom signal and specifies the args required.
request_audit_trail_signal = Signal()

logger = logging.getLogger(__name__)

# helper func that gets the client ip


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@receiver(request_audit_trail_signal)
def user_request_log_audit_trail(user, request, model, event_category, method, summary, **kwargs):
    try:
        endpoint = request.get_full_path()
        if '/admin/' not in endpoint:
            exec_time = kwargs.get('exec_time', '')
            user_agent_info = request.META.get(
                'HTTP_USER_AGENT', '<unknown>')[:255]
            detail = kwargs.get('detail', '')
            requestlog = UserRequestLog.objects.create(
                user=user,
                email=user.email,
                endpoint=endpoint,
                user_agent_info=user_agent_info,
                changed_object=model,
                event_category=event_category,
                login_IP=get_client_ip(request),
                is_deleted=False,
                action=method,
                change_summary=summary,
                detail=detail,
                exec_time=exec_time
            )
            logger.info(
                f"User request audit trail created {requestlog.id}  for user {requestlog.email} and object {requestlog.changed_object}")
    except Exception as e:

        logger.error("log_user_logged_in request: %s, error: %s" %
                     (request, e))


request_audit_trail_signal.connect(user_request_log_audit_trail)
