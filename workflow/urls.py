from django.conf.urls import patterns, url

from workflow.views import grid, log, delete

urlpatterns = patterns('',
    url(r'^$', grid),
    url(r'^grid/$', grid, name='grid'),
    url(r'^log/$', log, name='log'),
    url(r'^delete/(?P<rowid>\d+)/$', delete, name='delete'),
)

