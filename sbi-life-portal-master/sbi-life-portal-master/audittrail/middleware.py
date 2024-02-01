import logging
import time
import traceback

from django.utils.deprecation import MiddlewareMixin

from audittrail.signals import request_audit_trail_signal

logger = logging.getLogger(__name__)


class UserRequestAuditTrailMiddleware(MiddlewareMixin):

    def __call__(self, request, *args, **kwargs):
        # Exit out to async mode, if needed
        if self._is_coroutine:
            return self.__acall__(request)
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(request)
        self.execution_time = time.time()
        response = response or self.get_response(request)
        self.execution_time = time.time() - self.execution_time
        if hasattr(self, "process_response"):
            response = self.process_response(request, response)
        return response

    def process_exception(self, request, exception):
        # An exception occurred, send the audit trail signal with an error message
        # Get the view class and model as described above
        logger.info("process_exception called")
        view_class = self.get_view_class(request)

        model = self.get_model_from_view(view_class)

        # Build the error message from the traceback
        error_message = ''.join(traceback.format_tb(exception.__traceback__)) + "\n{}".format(str(exception))
        self.send_audit_trail_signal(request, view_class, model, error_message=error_message)

    def process_response(self, request, response):
        if 200 <= response.status_code < 400:
            self.handle_successful_response(request, response)
        else:
            self.handle_error_response(request, response)
        return response

    def handle_successful_response(self, request, response):
        logger.info("process_response called for successful response")
        view_class = self.get_view_class(request)
        model = self.get_model_from_view(view_class)
        self.send_audit_trail_signal(request, view_class, model, response)

    def handle_error_response(self, request, response):
        logger.info("process_response called for error response")
        view_class = self.get_view_class(request)
        model = self.get_model_from_view(view_class)
        error_message = traceback.format_exc()
        self.send_audit_trail_signal(request, view_class, model, response, error_message)

    def get_view_class(self, request):
        view_class = None
        resolver_match = request.resolver_match
        if resolver_match and resolver_match.func:
            if hasattr(request.resolver_match.func, 'cls'):
                view_class = request.resolver_match.func.cls
            elif hasattr(resolver_match.func, 'view_class'):
                view_class = resolver_match.func.view_class
        return view_class

    def get_model_from_view(self, view_class):
        if view_class and hasattr(view_class, 'model') and view_class.model:
            return view_class.model.__name__
        return None

    def send_audit_trail_signal(self, request, view_class, model, response=None, error_message=None):
        view_class_name = view_class.__name__ if view_class else None
        summary = "{} {}".format(request.method, request.path)
        if error_message:
            summary += " - ERROR"
        request_audit_trail_signal.send(
            sender=request.user.__class__,
            request=request,
            response=response,
            user=request.user,
            model=model,
            event_category=view_class_name,
            method=request.method,
            summary=summary,
            detail=error_message,
            exec_time=self.execution_time
        )
