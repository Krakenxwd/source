import binascii
import json
import os
import uuid
import datetime
import requests
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from claim_application.models import ApplicationDocument, MagicLinkHash
from claim_application.serializers import ProposalSerializer, MagicLinkSerializer
from claim_application.utils import stringify_data
from glib_sftp.models import SFTPConfiguration, SFTPRequest
from master.models import ExtractionConfiguration, MasterType, AccountConfiguration
from registration.custom_auth import CustomAuthentication
from registration.utils import get_domain, AesEncrDecrUtil


class BaseApiView(APIView):
    aes_encr_decr_obj = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ac = AccountConfiguration.objects.first()
        if ac:
            self.aes_encr_decr_obj = AesEncrDecrUtil(ac.secret_key, ac.salt_value)
        else:
            self.aes_encr_decr_obj = AesEncrDecrUtil("", "")

    def decrypt_data(self, encrypted_data):
        return self.aes_encr_decr_obj.decrypt(encrypted_data, self.aes_encr_decr_obj.SECRET_KEY,
                                              self.aes_encr_decr_obj.SALT_VALUE)

    def encrypt_data(self, decrypt_data):
        return self.aes_encr_decr_obj.encrypt(decrypt_data,
                                              self.aes_encr_decr_obj.SECRET_KEY,
                                              self.aes_encr_decr_obj.SALT_VALUE)

    def get_error_response_format(self, status_code, error_message):
        """
        Generate a formatted error response.

        Parameters:
        - status_code (int): The HTTP status code indicating the error.
        - error_message (str): The detailed error message.

        Returns:
        dict: A dictionary containing the formatted error response.
        """
        response_format = {
            "error": error_message
        }
        return {'status_code': status_code,
                'status': 'failed',
                'data': self.encrypt_data(json.dumps(response_format))}

    def get_success_response_format(self, status_code, response_format):
        """
        Generate a formatted success response.

        Parameters:
        - status_code (int): The HTTP status code indicating the success.
        - response_format (dict): The formatted response content.

        Returns:
        dict: A dictionary containing the formatted success response.
        """
        return {
            'status_code': status_code,
            'status': 'success',
            'data': self.encrypt_data(json.dumps(response_format))
        }


class CreateWorkOrder(BaseApiView):
    """
    This API is used to create work order.
    client will send required data in json format which is encrypted.
    """
    authentication_classes = [CustomAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProposalSerializer

    def post(self, request):
        try:
            request_data = request.data
            decrypted_data = self.decrypt_data(request_data.get('data'))

            if 'data' not in request_data:
                response_data = self.get_error_response_format(400, "Data is not in required format.")
                return JsonResponse(data=response_data, status=200)

            try:
                data = json.loads(decrypted_data.decode())
            except Exception:
                raise ValueError("400/decrypted data is not proper json format.")

            serializer = self.serializer_class(data=data)
            if not serializer.is_valid():
                error_msg = list(serializer.errors.values())[0][0]
                if isinstance(error_msg, dict):
                    error_msg = list(error_msg.values())[0][0]
                response_data = self.get_error_response_format(400, error_msg)
                return JsonResponse(data=response_data, status=200)

            data = stringify_data(serializer.data)
            policy_number = data.get('policy_number')
            proposal_number = data.get('proposal_number')
            date_of_intimation = datetime.datetime.strptime(data.get('date_of_intimation'), '%d/%m/%Y').date()
            configuration = ExtractionConfiguration.objects.first()
            application_type = data.get('application_type', '')
            master_type = MasterType.objects.filter(code=application_type.strip()).first() if application_type else None

            application_doc = ApplicationDocument.objects.create(
                name='merged.pdf',
                mode=ApplicationDocument.SFTP,
                policy_number=policy_number,
                proposal_number=proposal_number,
                date_of_intimation=date_of_intimation,
                configuration=configuration,
                master_type=master_type,
                created_by=self.request.user,
                digital_json_data=data
            )
            application_doc.log_task_submitted()
            sftp_configuration = SFTPConfiguration.objects.filter(active=True)
            response_data = self.call_sftp(sftp_configuration, application_doc)
        except Exception as e:
            if str(e).__contains__("/"):
                s_code, s_error = str(e).split('/')
            else:
                s_code, s_error = 400, str(e)
            response_data = self.get_error_response_format(s_code, s_error)
        return JsonResponse(data=response_data, status=200)

    def call_sftp(self, sftp_configuration, application_doc):
        """
        If sftp configurations exists call sftp event else return error message and deleted the failes document.
        """
        if sftp_configuration.exists():
            sftp_request = SFTPRequest(sftp_configuration=sftp_configuration.first())
            sftp_request.save()
            sftp_request.get_files(application_doc.policy_number, application_doc.id)
            return self.handle_sftp_response(sftp_request, application_doc)

        application_doc.delete()
        return self.get_error_response_format(406, "The request made is correct but SFTP not configured.")

    def handle_sftp_response(self, sftp_request, application_doc):
        """
        If sftp request goes on error delete the doc and return error response.
        Else return success response.
        """
        if sftp_request.status == SFTPRequest.ERROR:
            application_doc.delete()
            return self.get_error_response_format(400, sftp_request.message)

        return self.get_success_response_format(200, {
            "status": "success",
            "glib_id": str(application_doc.id),
            "policy_number": application_doc.policy_number
        })


class GetMagicLink(BaseApiView):
    """
    This API is used to get magic link.
    """
    authentication_classes = [CustomAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MagicLinkSerializer

    @staticmethod
    def create_user_and_magic_hash(data, application_doc_id):
        application_doc = ApplicationDocument.objects.get(id=application_doc_id)
        email = data.get('userId') + '@sbilife.co.in'
        defaults = {
            'password': binascii.hexlify(os.urandom(20)).decode()
        }

        group_obj, created = Group.objects.get_or_create(name='apiuser')
        user_obj, created = User.objects.get_or_create(username=email, email=email, defaults=defaults)
        user_obj.groups.add(group_obj)
        magic_hash = uuid.uuid4().hex
        obj, created = MagicLinkHash.objects.update_or_create(document=application_doc, user=user_obj,
                                                              defaults={'magic_hash': magic_hash})
        return obj

    def post(self, request):
        try:
            request_data = request.data
            current_site = get_domain()

            if 'data' not in request_data:
                response_data = self.get_error_response_format(400, "Data is not in required format.")
                return JsonResponse(data=response_data, status=200)

            decrypted_data = self.decrypt_data(request.data.get('data'))

            try:
                data = json.loads(decrypted_data.decode())
            except Exception:
                raise ValueError("400/decrypted data is not proper json format.")

            serializer = self.serializer_class(data=data)
            if not serializer.is_valid():
                error = list(serializer.errors.values())[0][0]
                response_data = self.get_error_response_format(400, error)
                return JsonResponse(data=response_data, status=200)

            data = stringify_data(serializer.data)
            policy_number = data.get('policy_number')
            application_doc = ApplicationDocument.objects.filter(policy_number=policy_number).first()
            magic_link_hash = self.create_user_and_magic_hash(data, application_doc.id)
            response_format = {
                "status": "success",
                "glib_id": str(application_doc.id),
                "magic_link": "{}{}".format(current_site, magic_link_hash.get_magic_link_url())
            }
            response_data = self.get_success_response_format(200, response_format)
        except Exception as e:
            if str(e).__contains__("/"):
                s_code, s_error = str(e).split('/')
            else:
                s_code, s_error = 400, str(e)
            response_data = self.get_error_response_format(s_code, s_error)
        return JsonResponse(data=response_data, status=200)
