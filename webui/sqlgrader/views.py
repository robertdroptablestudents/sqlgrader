from django.http import HttpResponseRedirect

def rootRedirect(request):
    return HttpResponseRedirect('/instructor/')