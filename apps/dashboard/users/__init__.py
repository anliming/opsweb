# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import ListView, DetailView,TemplateView
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect,QueryDict
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth.models import Permission,Group
from dashboard.models import UserProfile
from books.forms import  UserForm,UserUpdataForm
from django.contrib.auth.hashers import make_password
import json
from random import Random
from utils.gitlab_utils import gl
#from SendEmail import send_register_email

import logging

logger = logging.getLogger("opsweb")
class UserListView(LoginRequiredMixin,PaginationMixin,ListView):
    template_name = "dashboard/user_list.html"
    model = UserProfile
    paginate_by = 5
    context_object_name = "userlist"
    keyword = ""
    next_url = "/dashboard/userlist"

    def get_queryset(self):
        self.keyword = self.request.GET.get("keyword","")
        queryset = super(UserListView,self).get_queryset()
        if self.keyword:
            queryset = queryset.filter(Q(username__icontains=self.keyword)|
                                       Q(name_cn__icontains=self.keyword))
        return queryset
    def get_context_data(self, **kwargs):
        context = super(UserListView,self).get_context_data(**kwargs)
        context["keyword"] = self.keyword
        return context
    def delete(self,request,*args,**kwargs):
        try:
            user = self.model.objects.get(pk=QueryDict((request.body))["id"])
            #user = self.model.objects.get(pk=QueryDict((request.body))["id"]).delete()
            username = user.username
            user_id = gl.users.search(username)[0].id
            gl.users.delete(user_id)
            user.delete()
            ret = {"code": 0, "result": "删除用户成功", "next_url": self.next_url}
        except Exception as e:
            ret = {"code": 1, "errmsg": "删除用户失败,%s"%e.msg , "next_url": self.next_url}
        #return render(request,settings.JUMP_PAGE,ret)
        return JsonResponse(ret, safe=True)

    def post(self,request):
        form = UserForm(request.POST)
        if form.is_valid():
            user_pass = self.random_str()

            try:
                uname = request.POST.get("username","")
                uname_cn = request.POST.get("name_cn","")
                uemail = request.POST.get("email","")
                send_mail("平台通知","欢迎加入OPS平台。\r以下是你的账号信息:\r用户名:"+uname+"\r密码: "+user_pass +"\r平台地址:  http://ops.yktour.com.cn:8000/\r", settings.EMAIL_FROM,[uemail,])
                user = UserProfile()
                user.username = uname
                user.name_cn = uname_cn
                user.email = uemail
                user.phone = request.POST.get("phone","")
                user.set_password(user_pass)
                #send_mail("平台通知","欢迎加入OPS平台。\r以下是你的账号信息:\r用户名:"+uname+"\r密码: "+user_pass +"\r平台地址: %s http://ops.yktour.com.cn:8000/\r", "drachen@126.com",[uemail,])
                #send_register_email(email_title="平台通知", email_body="欢迎加入OPS平台。\r以下是你的账号信息:\r用户名: %s\r密码: %s\r平台地址: %s http://ops.yktour.com.cn:8000/\r"%(uname,user_pass), email_to=user.email)
                user.save()
                gl.users.create({"username":uname,"password":user_pass,"email":uemail,"name":uname_cn})
                ret = {"code": 0, "result": "添加用户成功", "next_url": self.next_url}
            except Exception as e:
                ret = {"code": 2, "errmsg": "添加失败", "next_url": self.next_url}
        else:
            ret = {"code": 1, "errmsg": "添加用户失败%s"%form.errors, "next_url": self.next_url}
        #return render(request,settings.JUMP_PAGE,ret)
        return JsonResponse(ret,safe=True)

    def random_str(self):
        str = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
        length = len(chars) - 1
        random = Random()
        for i in range(8):
            str += chars[random.randint(0, length)]
        return str

class UserDetailView(LoginRequiredMixin,DetailView):
    template_name = "dashboard/user_edit.html"
    model = UserProfile
    context_object_name = "user"
    next_url = "/dashboard/userlist/"
    def post(self,request,**kwargs):
        pk=kwargs.get("pk")
        form = UserUpdataForm(request.POST,instance=self.model.objects.get(pk=pk))
        if form.is_valid():
            try:
                form.save()
                ret = {"code": 0, "result": "更新用户成功", "next_url": self.next_url}
            except Exception as e:
                ret = {"code": 1, "result": "更新用户失败,%s"%e.msg, "next_url": self.next_url}
        else:
            ret = {"code": 1, "errmsg": form.errors, 'next_url': self.next_url}
        return render(request,settings.JUMP_PAGE,ret)

class ModifyPwdView(LoginRequiredMixin,TemplateView):
    template_name = "dashboard/change_passwd.html"
    model = UserProfile
    next_url = "/dashboard/userlist/"
    def get_context_data(self,**kwargs):
        context = super(ModifyPwdView,self).get_context_data(**kwargs)
        uid = self.request.GET.get("uid")
        context["uid"] = uid
        return context
    def post(self,request,*args,**kwargs):
        pk = request.POST.get("uid")
        user = self.model.objects.get(pk=pk)
        pwd1 = request.POST.get("password1")
        pwd2 = request.POST.get("password2")
        try:
            if pwd1 == pwd2:
                user.set_password(pwd1)
                user.save()
                ret = {"code":0,"result":"修改 %s 密码成功"%user.username,"next_url":self.next_url}
            else:
                ret = {"code": 1, "errmsg": "密码不一致","next_url":self.next_url}
        except Exception as e:
            ret = {"code": 1, "errmsg": e.msg, "next_url": self.next_url}
        return render(request,settings.JUMP_PAGE,ret)

class UserGroupPowerView(LoginRequiredMixin,DetailView):
    template_name = "dashboard/user_group_power.html"
    model = UserProfile
    next_url =  "/dashboard/userlist/"
    context_object_name = "user"
    def get_context_data(self, **kwargs):
        context = super(UserGroupPowerView,self).get_context_data(**kwargs)
        context["user_not_groups"] = self.user_not_groups()
        context["user_has_groups"] = self.user_has_groups()
        context["user_not_permissions"] = self.user_not_permissions()
        context["user_has_permissions"] = self.user_has_permissions()
        return context
    def user_not_groups(self):
        pk = self.kwargs.get("pk")
        not_groups = [group for group in Group.objects.all() if group not in self.user_has_groups()]
        return not_groups
    def user_not_permissions(self):
        pk = self.kwargs.get("pk")
        not_perms = [perm for perm in Permission.objects.all() if perm not in self.user_has_permissions()]
        return not_perms
    def user_has_groups(self):
        pk = self.kwargs.get("pk")
        groups = self.model.objects.get(pk=pk).groups.all()
        return groups
    def user_has_permissions(self):
        pk = self.kwargs.get("pk")
        perms = self.model.objects.get(pk=pk).user_permissions.all()
        return perms

    def post(self,request,*args,**kwargs):
        pk = request.POST.get("uid","")
        groups = request.POST.getlist("groups_selected",[])
        perms = request.POST.getlist("perms_selected",[])
        user = self.model.objects.get(pk=pk)
        try:
            user.groups = groups
            user.user_permissions = perms
            ret = {"code":0,"result":"修改用户角色权限成功","next_url":self.next_url}
        except Exception as e:
            ret = {"code": 1, "errmsg": e.msg, "next_url": self.next_url}
        return render(request,settings.JUMP_PAGE,ret)

