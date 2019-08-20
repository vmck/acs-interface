from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import UploadFileForm, LoginForm
from .backend.submission import handle_submission


def homepage(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'],
                                password=request.POST['password'])
            if user is not None:
                login(request, user)
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
