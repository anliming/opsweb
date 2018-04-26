"""opsweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from dashboard.views import LoginView, LogoutView, IndexView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^$', IndexView.as_view(), name='index'),
    url('^index/', IndexView.as_view(), name='index'),
    url('^login/', LoginView.as_view(), name='login'),
    url('^logout/', LogoutView.as_view(), name='logout'),
    url('^dashboard/', include("dashboard.urls", namespace="dashboard")),
    url('^work_order/', include('work_order.urls', namespace='work_order')),
    url('^cmdb/', include('cmdb.urls', namespace='cmdb')),
    url('^task/', include('tasks.urls', namespace='task')),
    url('^books/', include('books.urls', namespace='books')),
]
