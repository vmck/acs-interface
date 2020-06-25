from django import forms
from django.conf import settings


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Select archive',
        widget=forms.FileInput(attrs={'accept': 'application/zip'}),
    )


class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
