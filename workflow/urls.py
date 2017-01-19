from django.conf.urls import url

from workflow import views
from workflow import report

urlpatterns = [
    url(r'^$', views.grid),
    url(r'^grid/$', views.grid, name='grid'),
    url(r'^grid/(?P<mode>\w+)/$', views.grid, name='grid'),
    url(r'^about/$', views.about, name='about'),
    url(r'^report/$', report.report, name='report'),
    # DEPRECATED url(r'^delete/(?P<rowid>\d+)/$', views.delete, name='delete'),
    url(r'^delete_row_ajax/$', views.delete_row_ajax, name='delete_row_ajax'),
    url(r'^change_import/$', views.change_import, name='change_import'),
]