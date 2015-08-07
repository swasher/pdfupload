# coding: utf-8

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/', include('accounts.urls', namespace='accounts')),
    url(r'^', include('accounts.urls')),
    url(r'^', include('workflow.urls')),
    url(r'^', include('stanzforms.urls')),
    url(r'^', include('technologichka.urls')),

    url(r'^grappelli/', include('grappelli.urls')),  # grappelli URLS
    url(r'^admin/rq/', include('django_rq_dashboard.urls')),

    # DEPRECATED
    #url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    #url(r'^login/$', 'workflow.views.login', name='login'),
    #url(r'^logout/$', 'workflow.views.logout', name='logout'),
    #url(r'^login_redirect/$', 'workflow.views.login_redirect', name='login_redirect'),

)


# хз для чего это. вроде как чтобы media работало в dev time
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)