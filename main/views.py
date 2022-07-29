from django.shortcuts import render
from accounts.models import User

# Create your views here.
def showmain(request):
    context = {}

    login_session  = request.session.get('login_session', '')

    if login_session == '':
        context['login_session'] = False
    else:
        context['login_session'] = True

    return render(request, 'main/mainpage.html', context)