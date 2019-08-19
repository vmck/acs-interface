from django.shortcuts import render
from .forms import UploadFileForm


def homepage(request):
    if request.method == 'POST'and request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print('success')
    else:
        form = UploadFileForm()

    return render(request, 'interface/homepage.html', {'form': form})
