# _*_ coding: utf-8 _*_
from django.conf.urls import url
from .views import *

urlpatterns = [
    url('^apply/$', ApplyView.as_view(), name='apply'),
    url('^apply_list/$', ApplyListView.as_view(), name='apply_list'),
    url('^deploy/(?P<pk>[0-9]+)?/$',  DeployView.as_view(), name='deploy'),
    url('^deploy_history/$', DeployHistoryView.as_view(), name='deploy_history'),

    # 获取某个项目的所有标签(版本)
    url('^get_project_versions/$', GetProjectVersionsView.as_view(), name='get_project_versions'),
]