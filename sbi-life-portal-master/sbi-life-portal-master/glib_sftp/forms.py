import django.forms as forms

from glib_sftp.models import SFTPConfiguration


class CreateSFTPConfigurationForm(forms.ModelForm):
    host = forms.CharField(
        required=True,
        label='Host*'
    )
    port = forms.CharField(
        required=True,
        initial=22,
        label='Port*'
    )
    username = forms.CharField(
        required=True,
        label='Username*',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=True),
        required=True,
        label='Password*'
    )
    file_path = forms.CharField(
        required=True,
        label='File Path*'
    )
    supported_file_extension = forms.CharField(
        required=True,
        initial='pdf',
        label='Supported File Extension*'
    )
    active = forms.BooleanField(
        required=False,
        label='Active',
    )

    class Meta:
        model = SFTPConfiguration
        fields = ['host', 'port', 'username', 'password',
                  'file_path', 'upload_path', 'supported_file_extension', 'timezone', 'active']

    def __init__(self, *args, **kwargs):
        super(CreateSFTPConfigurationForm, self).__init__(*args, **kwargs)
        self.fields['active'].widget.attrs['id'] = 'switch'
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'border p-2 rounded-md w-full outline-none focus:ring-2 focus:ring-blue-300 focus:border-transparent'
        self.label_suffix = ""
