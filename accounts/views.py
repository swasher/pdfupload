# coding: utf-8

from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.shortcuts import RequestContext
from django.contrib import messages
from django.contrib.auth import login as django_login, authenticate, logout as django_logout


def login(request):
    context = RequestContext(request)
    if request.method == 'POST':
        username, password = request.POST['username'], request.POST['password']
        print('username', username)
        print('pass', password)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                django_login(request, user)
                messages.add_message(request, messages.SUCCESS, 'You are sucessfully login!')
            else:
                #context['error'] = 'Non active user'
                messages.add_message(request, messages.INFO, 'Non active user')
        else:
            messages.add_message(request, messages.INFO, 'Wrong username or password')
    return redirect('/')
    #return render_to_response('grid.html', ???)


def login_redirect(request):
    messages.add_message(request, messages.INFO, 'Вы должны быть зарегистрированны для выполнения этой операции.')
    return redirect('/')


def logout(request):
    django_logout(request)
    return redirect('/')
