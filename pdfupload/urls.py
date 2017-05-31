# coding: utf-8

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = [
    # deprecated url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/', admin.site.urls),

    url('^', include('django.contrib.auth.urls')),
    url(r'^accounts/', include('accounts.urls', namespace='accounts')),

    url(r'^', include('workflow.urls')),
    url(r'^', include('stanzforms.urls')),
    url(r'^', include('technologichka.urls')),

    #url(r'^grappelli/', include('grappelli.urls')),
    url(r'^django-rq/', include('django_rq.urls')),
]

# хз для чего это. вроде как чтобы media работало в dev time
#urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)