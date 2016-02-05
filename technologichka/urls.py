from django.conf.urls import patterns, url
from .views import orders, create_new_order, print_pdf_order, copy_order


urlpatterns = patterns('',
    url(r'^orders/$', orders, name='orders'),
    url(r'^create_new_order/$', create_new_order, name='create_new_order'),
    url(r'^print_pdf_order/(?P<orderid>\d+)/$', print_pdf_order, name='print_pdf_order'),
    url(r'^copy_order/(?P<orderid>\d+)/$', copy_order, name='copy_order'),
)
