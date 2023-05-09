from django.shortcuts import render
from django.conf import settings

def login_view(request, context={}):
    context['path'] = settings.STATIC_ROOT
    return render(request, 'login.html', context=context)