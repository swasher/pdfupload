from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('workflow.urls')),

    #url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^login/$', 'workflow.views.login', name='login'),
    url(r'^logout/$', 'workflow.views.logout', name='logout'),
    url(r'^login_redirect/$', 'workflow.views.login_redirect', name='login_redirect'),
)
