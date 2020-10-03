from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat


class UploadFileForm(forms.Form):
    file = forms.FileField(
        label="Select archive",
        widget=forms.FileInput(attrs={"accept": "application/zip"}),
    )

    def clean_file(self):
        data = self.cleaned_data["file"]

        if data.size >= settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
            raise forms.ValidationError(
                "Keep files below "
                f"{filesizeformat(settings.FILE_UPLOAD_MAX_MEMORY_SIZE)}"
            )

        return data


class LoginForm(forms.Form):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
