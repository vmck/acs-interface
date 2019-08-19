from django.shortcuts import render
from .forms import UploadFileForm
from .submission import handle_submission


def homepage(request):
    if request.method == 'POST'and request.FILES:
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_submission(request.FILES['file'])
    else:
        form = UploadFileForm()

    return render(request, 'interface/homepage.html', {'form': form})
