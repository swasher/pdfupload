from django.conf.urls import patterns, url
from technologichka import views


urlpatterns = [
    url(r'^orders/$', views.orders, name='orders'),
    url(r'^create_new_order/$', views.create_new_order, name='create_new_order'),
    url(r'^print_pdf_order/(?P<orderid>\d+)/$', views.print_pdf_order, name='print_pdf_order'),
    url(r'^copy_order/(?P<orderid>\d+)/$', views.copy_order, name='copy_order'),
]