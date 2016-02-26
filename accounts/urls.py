# coding: utf-8
from django.conf.urls import url
from accounts.views import login
from accounts.views import login_redirect

urlpatterns = [
    url(r'^login/$', login, name='login'),
    url(r'^login_redirect(?P<next>\w+)/$', login_redirect, name='login_redirect'),
]