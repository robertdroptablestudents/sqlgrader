from django.http import HttpResponseRedirect

def rootRedirect(request):
    return HttpResponseRedirect('/instructor/')

def reportRedirect(request):
    return HttpResponseRedirect('/report_builder/')