from django.shortcuts import  render
from django.contrib import messages

def multiple_file_upload(request):
    template_name = "badge/test/test.html"  # Replace with your template.
    if request.method == 'POST':
        messages.warning(request,"Controllare i campi errati!")
        keys=request.FILES.keys()
        #loop sui file
        for file_key in keys:
            file_da_elaborare=request.FILES.get(file_key)
    return render(request,template_name)
        