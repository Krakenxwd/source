import binascii
import os
import uuid

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from claim_application.models import ApplicationDocument, MagicLinkHash
from claim_application.utils import call_sbilife_authenticate_user


class HolderSerializer(serializers.Serializer):
    client_id = serializers.IntegerField()
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    relatives_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    dob = serializers.DateField(required=False, input_formats=["%d/%m/%Y", ""], format='%d/%m/%Y', allow_null=True,
                                error_messages={
                                    'invalid': 'dob is not a valid date allowed format is dd/mm/yyyy.',
                                })
    expiry_date = serializers.DateField(required=False, input_formats=["%d/%m/%Y", ""], format='%d/%m/%Y',
                                        allow_null=True, error_messages={
            'invalid': 'expiry_date is not a valid date allowed format is dd/mm/yyyy.',
        })
    gender = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    contact_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pan_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    aadhar_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    voter_id_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    driving_license_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    passport_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address_1 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address_2 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    address_3 = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    state = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    city = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    pincode = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def __init__(self, *args, **kwargs):
        super(HolderSerializer, self).__init__(*args, **kwargs)
        self.fields['client_id'].error_messages['blank'] = u'client_id cannot be blank.'
        self.fields['client_id'].error_messages['required'] = u'client_id is required.'


class NomineeSerializer(HolderSerializer):
    ifsc_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    branch_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bank_account_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    name_of_bank = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ProposalSerializer(serializers.Serializer):
    proposal_number = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    policy_number = serializers.CharField(validators=[
        UniqueValidator(queryset=ApplicationDocument.objects.all(),
                        message='Record with such policy number already exists.')])
    application_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date_of_intimation = serializers.DateField(input_formats=["%d/%m/%Y"], format='%d/%m/%Y', error_messages={
        'invalid': 'date_of_intimation is not a valid date. Allowed format is dd/mm/yyyy.',
    })
    policy_holder_detail = HolderSerializer(many=True, required=False)
    policy_nominees_detail = NomineeSerializer(many=True, required=False)

    def __init__(self, *args, **kwargs):
        super(ProposalSerializer, self).__init__(*args, **kwargs)
        self.fields['policy_number'].error_messages['blank'] = u'policy_number cannot be blank.'
        self.fields['policy_number'].error_messages['required'] = u'policy_number is required.'
        self.fields['date_of_intimation'].error_messages['blank'] = u'date_of_intimation cannot be blank.'
        self.fields['date_of_intimation'].error_messages['required'] = u'date_of_intimation is required.'


class MagicLinkSerializer(serializers.Serializer):
    policy_number = serializers.CharField()
    tokenId = serializers.CharField()
    userId = serializers.CharField()
    application = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super(MagicLinkSerializer, self).__init__(*args, **kwargs)
        self.fields['policy_number'].error_messages['blank'] = u'policy_number cannot be blank.'
        self.fields['policy_number'].error_messages['required'] = u'policy_number is required.'

    def validate(self, data):
        policy_number = data.get('policy_number')
        application_doc = ApplicationDocument.objects.filter(policy_number=policy_number)
        if not application_doc.exists():
            raise serializers.ValidationError("No application found.")
        status_code = call_sbilife_authenticate_user(data)
        if 200 not in [status_code]:
            raise serializers.ValidationError("user does not exist in our system.")
        return data
