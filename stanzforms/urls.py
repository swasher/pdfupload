from django.conf.urls import url

#from .views import doska_list, knife_list
from stanzforms import views

urlpatterns =[
    url(r'^doska_list/$', views.doska_list, name='doska_list'),
    url(r'^knife_list/(?P<doskaid>\d+)/$', views.knife_list, name='knife_list'),
]
