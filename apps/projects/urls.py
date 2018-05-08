# _*_ coding: utf-8 _*_

from django.conf.urls import url
from .views import *

urlpatterns = [
    url('^list/$', ProjectListView.as_view(), name='project_list'),
    url('^add/$', ProjectAddView.as_view(), name='project_add'),
]
