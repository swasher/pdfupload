from django.conf.urls import url

import views
import report

urlpatterns = [
    url(r'^$', views.grid),
    url(r'^grid/$', views.grid, name='grid'),
    url(r'^grid/(?P<mode>\w+)/$', views.grid, name='grid'),
    url(r'^about/$', views.about, name='about'),
    url(r'^report/$', report.report, name='report'),
    url(r'^log/$', views.log, name='log'),
    url(r'^usersettings/$', views.usersettings, name='usersettings'),
    url(r'^delete/(?P<rowid>\d+)/$', views.delete, name='delete'),
    url(r'^change_import/$', views.change_import, name='change_import'),
]
