from django.shortcuts import render, redirect
from interface.forms import UploadFileForm, LoginForm
from interface.backend.submission import handle_submission


def homepage(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            return redirect(upload)
    else:
        form = LoginForm()

    return render(request, 'interface/homepage.html', {'form': form})


def upload(request):
    if request.method == 'POST'and request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_submission(request)
    else:
        form = UploadFileForm()

    return render(request, 'interface/upload.html', {'form': form})
