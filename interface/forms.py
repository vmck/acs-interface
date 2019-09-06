from django import forms


class UploadFileForm(forms.Form):
    assignment_id = forms.CharField(label='',
                                    widget=forms.Select(choices=[('pc-00', 'Programarea Calculatoarelor - Tema 1')]))  # noqa: E501
    file = forms.FileField(label='Select archive',
                           widget=forms.FileInput(attrs={'accept': 'application/zip'}))  # noqa: E501


class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
