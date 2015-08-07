from django.conf.urls import patterns, url

from .views import doska_list, knife_list

urlpatterns = patterns('',
    # url(r'^$', doska_list),
    url(r'^doska_list/$', doska_list, name='doska_list'),
    url(r'^knife_list/(?P<doskaid>\d+)/$', knife_list, name='knife_list'),
)
