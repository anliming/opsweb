from django.conf.urls import  url

from .views import  *

urlpatterns = [
    url('^add/$', TaskAddView.as_view(), name='add'),
    url('^add1/$', TaskAdd1View.as_view(), name='add1'),
    url('^edit/(?P<pk>[0-9]+)?/$', TaskEditView.as_view(), name='edit'),
    url('^list/$', TaskListView.as_view(), name='list'),
    url('^detail/(?P<pk>[0-9]+)?/$', TaskDetailView.as_view(),name='detail'),
]