# coding: utf-8

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import login as django_login, authenticate


def login(request):
    if request.method == 'POST':
        username, password = request.POST['username'], request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                django_login(request, user)
                messages.add_message(request, messages.SUCCESS, 'You are sucessfully login!')
            else:
                #context['error'] = 'Non active user'
                messages.add_message(request, messages.WARNING, 'Non active user')
        else:
            messages.add_message(request, messages.ERROR, 'Wrong username or password')
    else:
        messages.add_message(request, messages.ERROR, 'Вы должны быть зарегистрированны для выполнения этой операции.')
    return redirect('/')
