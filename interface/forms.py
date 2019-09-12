from django import forms

from interface.models import Assignment


def get_assignments():
    choices = []

    for assignment in Assignment.objects.all():
        choices.append((assignment.code, assignment.name))

    return choices


class UploadFileForm(forms.Form):
    assignment_id = forms.CharField(label='',
                                    widget=forms.Select(choices=get_assignments(), attrs={'class': 'custom-select'}))  # noqa: E501
    file = forms.FileField(label='Select archive',
                           widget=forms.FileInput(attrs={'accept': 'application/zip'}))  # noqa: E501


class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
