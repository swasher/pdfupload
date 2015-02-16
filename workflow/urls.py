from django.conf.urls import patterns, url

from workflow.views import grid, log, delete, usersettings
from workflow.report import report
from workflow.tests import test

urlpatterns = patterns('',
    url(r'^$', grid),
    url(r'^grid/$', grid, name='grid'),
    url(r'^grid/(?P<mode>\w+)/$', grid, name='grid'),
    url(r'^report/$', report, name='report'),
    url(r'^test/$', test, name='test'),
    url(r'^log/$', log, name='log'),
    url(r'^usersettings/$', usersettings, name='usersettings'),
    url(r'^delete/(?P<rowid>\d+)/$', delete, name='delete'),
)


