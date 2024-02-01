import ast
import json

from django.contrib import messages
from django.core.management import get_commands, call_command
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from master.models import AccountConfiguration
from mixins.views import GroupRequiredMixin
from registration.utils import AesEncrDecrUtil


# Create your views here.
class RunManagementCommandView(GroupRequiredMixin, TemplateView):
    template_name = 'master/run_command.html'

    def get_context_data(self, **kwargs):
        context = super(RunManagementCommandView, self).get_context_data(**kwargs)
        commands = get_commands()
        context['applications'] = list(set(commands.values()))
        context['commands'] = json.dumps(commands)
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            result = ''
            arguments = {}
            post_data = dict(request.POST)
            del post_data['csrfmiddlewaretoken']
            if all(x in list(post_data.keys()) for x in ['command', 'extra-items']):
                command = post_data.get('command', '')[0]
                extra_items = post_data.get('extra-items', '')
                if extra_items:
                    arguments = ast.literal_eval(extra_items[0])
                result = call_command(command, **arguments)
            messages.success(request, str(result))
        except Exception as e:
            messages.warning(request, str(e))
        return redirect(reverse('master:run.management'))


class EncDecryptView(GroupRequiredMixin, TemplateView):
    template_name = 'master/encdecrypt.html'


class GetEncDecrAjaxView(GroupRequiredMixin, View):
    aes_encr_decr_obj = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ac = AccountConfiguration.objects.first()
        if ac:
            self.aes_encr_decr_obj = AesEncrDecrUtil(ac.secret_key, ac.salt_value)
        else:
            self.aes_encr_decr_obj = AesEncrDecrUtil("", "")

    def post(self, request, *args, **kwargs):
        try:
            response_data = {}
            req_data = dict(request.POST)
            plain_txt = req_data['simpleOutputTxt'][0] if req_data.get('simpleOutputTxt', []) else []
            enctxt = req_data['encText'][0] if req_data.get('encText', []) else []
            ac = AccountConfiguration.objects.first()
            if ac:
                if plain_txt or enctxt:
                    result = {
                        "decrData": self.aes_encr_decr_obj.decrypt(enctxt, ac.secret_key,
                                                                   ac.salt_value).decode() if enctxt else "",
                        "encData": self.aes_encr_decr_obj.encrypt(plain_txt, ac.secret_key,
                                                                  ac.salt_value) if plain_txt else ""}
                    response_data['data'] = result
                    response_data['code'] = 1
                else:
                    response_data['code'] = -1
                    response_data['msg'] = 'Encrytion Decryption text cannot be empty.'
            else:
                response_data['code'] = -1
                response_data['msg'] = 'Account configuration is not defined.'
        except Exception as e:
            response_data = {
                'code': -1,
                'msg': str(e)
            }
            print("Error: ", str(e))
        return JsonResponse(response_data)
