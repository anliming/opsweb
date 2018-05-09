# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import ListView, DetailView,TemplateView,View
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect,QueryDict,HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.models import Permission,Group
from dashboard.models import UserProfile
from books.forms import  GroupForm,GroupUpdateForm
from utils.gitlab_utils import gl

class GroupListView(LoginRequiredMixin,PaginationMixin,ListView):
    template_name = "dashboard/group_list.html"
    model = Group
    context_object_name = "grouplist"
    paginate_by = 5

    def post(self,request):
        form = GroupForm(request.POST)
        try:
            #Group.objects.create(name=request.POST.get("name"))
            if form.is_valid():
                form.save()
                ret = {"code":0,"result":"添加角色成功"}
                gname = request.POST.get("name")
                print(gname)
                gl.groups.create({'name': gname, 'path': gname})
            else:
                ret = {"code": 1, "errmsg": form.errors}
        except Exception as e:
            ret = {"code":1,"errmsg":e.msg}
        return JsonResponse(ret,safe=True)

    def delete(self,request):
        pk = QueryDict(request.body).get("id","")
        group = self.model.objects.get(pk=pk)
        try:
            if group.user_set.all() or group.permissions.all():
                ret = {"code": 1, "errmsg": "角色有成员或有权限在内"}
            else:
                #groupname = group[0].name
                groupname = group.name
                #group_id = gl.groups.search(groupname)[0].id
                #print(groupname,group_id)
                #gl.groups.delete(group_id)
                group.delete()
                ret = {"code":0,"result":"删除角色成功"}
        except Exception as e:
            ret = {"code": 1, "errmsg": e.msg}
        return JsonResponse(ret,safe=True)
class GroupDetailView(LoginRequiredMixin,DetailView):
    template_name = "dashboard/group_edit.html"
    model = Group
    context_object_name = "group"
    next_url = "/dashboard/grouplist"
    def get_context_data(self, **kwargs):
        context = super(GroupDetailView,self).get_context_data(**kwargs)
        context["group_has_permissions"] = self.get_have_permissions()
        context["group_not_permissions"] = self.get_not_permissions()
        return context
    def get_have_permissions(self):
        pk = self.kwargs.get("pk")
        return  self.model.objects.get(pk=pk).permissions.all()
    def get_not_permissions(self):
        perms = [perm for perm in Permission.objects.all() if perm not in self.get_have_permissions()]
        return perms
    def post(self,request,*args,**kwargs):
        gid = request.POST.get("gid","")
        perms = request.POST.getlist("perms_selected",[])
        name = request.POST.get("name","")
        group = self.model.objects.get(pk=gid)
        try:
            group.permissions = perms
            group.name = name
            group.save()
            ret = {"code": 0, "result": "更新角色成功","next_url":self.next_url}
        except Exception as e:
            ret = {"code": 1, "errmsg": e.msg, "next_url": self.next_url}
        return render(request,settings.JUMP_PAGE,ret)

class GroupUsersView(LoginRequiredMixin,View):
        def get(self,*args,**kwargs):
            users = Group.objects.get(pk=self.request.GET.get("gid","")).user_set.all()
            user_list = [{"username":user.username,"name_cn":user.name_cn,"email":user.email,"id":user.id} for user in users]
            return JsonResponse(user_list,safe=False)
        def delete(self,request,*args,**kwargs):
            data = QueryDict(request.body)
            group = Group.objects.get(pk=data.get("groupid",""))
            user = UserProfile.objects.get(pk=data.get("userid",""))
            try:
                user.groups.remove(group)
                ret = {"code":0,"result":"删除用户成功"}
            except Exception as e:
                ret = {"code":1,"errmsg":e.msg}
            return JsonResponse(ret)

