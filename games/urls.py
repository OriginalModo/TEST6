from django.urls import re_path
from . import views

urlpatterns = [
    re_path(r'^create/$', views.order_create, name='order_create'),
    re_path(r'^$', views.order_list, name='order_list'),
]