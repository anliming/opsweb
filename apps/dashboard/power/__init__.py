# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect,QueryDict
from django.core.urlresolvers import reverse
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.models import Permission,Group
from dashboard.models import UserProfile
from books.forms import  PowerForm,PowerUpdateForm


class PowerListView(LoginRequiredMixin,PaginationMixin,ListView):
    template_name = "dashboard/power_list.html"
    model = Permission
    context_object_name = "powerlist"
    paginate_by = 5
    keyword=""
    def get_queryset(self):
        queryset = super(PowerListView,self).get_queryset()
        self.keyword = self.request.GET.get('keyword','').strip()
        queryset = queryset.filter(Q(name__icontains=self.keyword) |
                                   Q(codename__icontains=self.keyword))
        return queryset
    def get_context_data(self,**kwargs):
        context = super(PowerListView,self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context
    def post(self,request):
        form = PowerForm(self.request.POST)
        if form.is_valid():
            form.save()
            res = {'code': 0, 'result': '添加权限成功'}
        else:
            res = {'code': 1, 'errmsg': form.errors}
        return JsonResponse(res, safe=True)

    def delete(self,request,**kwargs):
        power = self.model.objects.get(pk=QueryDict(request.body)["id"])
        try:
            if power.user_set.all() or power.group_set.all():
                res = {'code': 1, 'errmsg': '权限已被占用，删除失败'}
            else:
                power.delete()
                res = {'code': 0, 'result': '删除权限成功'}
        except Exception as e:
            res = {'code': 1, 'errmsg': '删除权限失败，%s'%e.msg}
        return JsonResponse(res,safe=True)

class PowerDetailView(LoginRequiredMixin,DetailView):
    template_name = "dashboard/power_edit.html"
    model = Permission
    context_object_name = "power"
    next_url = "/dashboard/powerlist"
    def post(self,request,*args,**kwargs):
        pk = kwargs.get("pk")
        p = self.model.objects.get(pk=pk)
        form = PowerUpdateForm(request.POST,instance=p)
        if form.is_valid():
            form.save()
            res = {'code': 0, 'result': '更新权限成功','next_url':self.next_url}
        else:
            res = {'code': 1, 'errmsg': form.errors,'next_url':self.next_url}
        return render(request, settings.JUMP_PAGE, res)