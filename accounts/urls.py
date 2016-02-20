from django.conf.urls import url

from accounts import views

urlpatterns = [
    url(r'^login/$', views.login, name='login'),
    #url(r'^login/(?P<next>\w+)/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    #url(r'^login_redirect/$', views.login_redirect, name='login_redirect'),
    url(r'^login_redirect/(?P<next>\w+)/$', views.login_redirect, name='login_redirect'),
]