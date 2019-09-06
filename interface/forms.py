from django.conf import settings
from django import forms

import requests
import configparser


def get_assignments():
    setup_data = requests.get(settings.SETUP_ASSIGNMENT_URL)

    config = configparser.ConfigParser()
    config.read_string(setup_data.text)

    choices = []

    for assignment in config.sections():
        choices.append((assignment, config[assignment]['name']))

    return choices


class UploadFileForm(forms.Form):
    assignment_id = forms.CharField(label='',
                                    widget=forms.Select(choices=get_assignments()))  # noqa: E501
    file = forms.FileField(label='Select archive',
                           widget=forms.FileInput(attrs={'accept': 'application/zip'}))  # noqa: E501


class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
