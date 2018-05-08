#coding=utf-8
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required, permission_required
from .views import *

urlpatterns = [
    url(r'^inception_result/(?P<pk>\d+)?/?(?P<actiontype>\w+)?$', inception_result.as_view(), name='inception_result'),
    url(r'^inception_check/', inception_check.as_view(), name='inception_check'),
    url(r'^autoselect/', autoselect.as_view(), name='autoselect'),
    url(r'^optimize_check/', optimize_check.as_view(), name='optimize_check'),
    url(r'^optimize_result/(?P<pk>\d+)?/?$', optimize_result.as_view()),
    url(r'^dbconfig/(?P<pk>\d+)?/?$', dbconfig.as_view(), name='dbconfig'),

]

