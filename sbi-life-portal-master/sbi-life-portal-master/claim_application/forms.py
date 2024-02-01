import django.forms as forms
from django.core.exceptions import ValidationError
from django.forms import ClearableFileInput, CheckboxInput
from django.forms.fields import FileField

from claim_application.models import ApplicationDocument
from master.models import MasterType

FILE_INPUT_CONTRADICTION = object()


class ClearableMultipleFilesInput(ClearableFileInput):
    def value_from_datadict(self, data, files, name):
        upload = files.getlist(name)  # files.get(name) in Django source

        if not self.is_required and CheckboxInput().value_from_datadict(
                data, files, self.clear_checkbox_name(name)):

            if upload:
                return FILE_INPUT_CONTRADICTION
            return False
        return upload


class MultipleFilesField(FileField):
    widget = ClearableMultipleFilesInput

    def clean(self, data, initial=None):
        if data is FILE_INPUT_CONTRADICTION:
            raise ValidationError(self.error_messages['contradiction'], code='contradiction')
        if data is False:
            if not self.required:
                return False
            data = None
        if not data and initial:
            return initial
        return data


class UploadDocumentForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(UploadDocumentForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs['multiple'] = True

    file = MultipleFilesField(
        widget=ClearableMultipleFilesInput(
            attrs={'accept': 'application/pdf,image/x-png,image/jpeg,image/tiff,image/tif', }))

    policy_number = forms.CharField(max_length=255, required=True)
    document_type = forms.ModelChoiceField(queryset=MasterType.objects.filter(is_active=True), initial=0)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    def clean_policy_number(self):
        policy_number = self.cleaned_data.get('policy_number', '')
        if ApplicationDocument.objects.filter(policy_number=policy_number).exists():
            self._errors['policy_number'] = self.error_class(
                ['Record with such policy number already exists.'])
        return self.cleaned_data.get('policy_number', '')

    def clean_file(self):
        files = self.cleaned_data.get('file', '')
        ext = ['png', 'jpeg', 'tiff', 'tif', 'pdf', 'jpg']
        if files:
            size = 0
            for file in files:
                size += file.size
            if not any(file.name.split('.')[-1].lower() in ext for file in files):
                self._errors['file'] = self.error_class(
                    ['Invalid file format.'])
            elif size > 1048576 and round(size / 1048576, 2) > 100:
                self._errors['file'] = self.error_class(
                    ['Selected files are larger than 100 mb.'])
        return self.cleaned_data.get('file', '')


class ApplicationHolderNomineeForm(forms.Form):
    MALE = 'male'
    FEMALE = 'female'
    HOLDER = 'holder'
    NOMINEE = 'nominee'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    ENTITY_CHOICES = (
        (HOLDER, 'Policy Holder'),
        (NOMINEE, 'Policy Nominee'),
    )
    entity_type = forms.ChoiceField(choices=ENTITY_CHOICES)
    customer_id = forms.CharField(max_length=100,
                                  widget=forms.TextInput(attrs={'class': 'text-red-500', 'required': 'required'}))
    number = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'text-red-500'}))
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'text-red-500'}))
    dob = forms.DateField(input_formats={'%d/%m/%Y'},
                          widget=forms.DateInput(attrs={'class': 'text-red-500', 'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    address = forms.CharField(max_length=255)
    name_of_bank = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'text-red-500'}))
    account_no = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'text-red-500'}))


ApplicationHolderNomineeFormSet = forms.formset_factory(ApplicationHolderNomineeForm, extra=1)
