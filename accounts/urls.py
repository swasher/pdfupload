__author__ = 'swasher'

from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^login/$', 'accounts.views.login', name='login'),
    # url(r'^login/(?P<next>\w+)/$', 'accounts.views.login', name='login'),
    url(r'^logout/$', 'accounts.views.logout', name='logout'),
    url(r'^login_redirect/$', 'accounts.views.login_redirect', name='login_redirect'),
)