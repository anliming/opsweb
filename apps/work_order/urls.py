# _*_ coding: utf-8 _*_
from django.conf.urls import url
from .views import *

urlpatterns = [
    url('^apply/$', WorkOrderApplyView.as_view(), name='apply'),
    url('^list/$', WorkOrderListView.as_view(), name='list'),
    url('^detail/(?P<pk>[0-9]+)?/$', WorkOrderDetailView.as_view(), name='detail'),
    url('^history/$', WorkOrderHistoryView.as_view(), name='history'),
<<<<<<< HEAD
    url('^daily/$', WorkOrderDailyView.as_view(), name='daily'),
    url('^test/$', TestEcharts.as_view(), name='testecharts'),

=======
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
]
