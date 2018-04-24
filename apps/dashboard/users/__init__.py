<<<<<<< HEAD
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
            user = self.model.objects.get(pk=QueryDict((request.body))["id"]).delete()
            ret = {"code": 0, "result": "删除用户成功", "next_url": self.next_url}
        except Exception as e:
            ret = {"code": 1, "errmsg": "删除用户失败,%s" , "next_url": self.next_url}
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
=======
#coding:utf-8
from django.shortcuts import render
from django.http import  HttpResponseRedirect,JsonResponse,QueryDict,Http404
from django.core.urlresolvers import reverse
from django.views.generic import View, ListView, DetailView
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission, Group
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


# 自定义模块导入
from dashboard.models import UserProfile
from dashboard.forms import UserProfileForm
from django.conf import settings
from pure_pagination.mixins import PaginationMixin

import traceback,json,logging

logger = logging.getLogger("opsweb")


class UserListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
        查看所有用户:只有指定权限的用户可看
    """
    model = UserProfile
    template_name = 'dashboard/user_list.html'
    context_object_name = "userlist"
    paginate_by = 5
    keyword = ''

    def get_queryset(self):
        queryset = super(UserListView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(name_cn__icontains=self.keyword)|
                                        Q(username__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

    @method_decorator(permission_required('dashboard.admin', login_url='/'))
    def get(self, request, *args, **kwargs):
        return super(UserListView,self).get(request, *args, **kwargs)


    """
        创建用户
    """
    @method_decorator(permission_required('dashboard.admin', login_url='/'))
    def post(self, request):
        username = request.POST.get('username', '')
        name_cn = request.POST.get('name_cn', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        password = make_password("12345678")

        try:
            user = UserProfile()
            user.username = username
            user.name_cn = name_cn
            user.email = email
            user.phone = phone
            user.password = password
            user.is_active = True
            user.save()

            # 创建gitlab账户
            '''
            user = gl.users.create({'username': username,
                                    'password': "12345678",
                                    'email': email,
                                    'name': name})
            print user
            '''
            res = {'code': 0, 'result': '添加用户 {0} 成功，用户名密码已经发送到 {1} 邮箱!'.format(name_cn, email)}
        except:
            logger.error("create user  error: %s" % traceback.format_exc())
            res = {'code': 1, 'errmsg': '添加用户失败'}
        return JsonResponse(res, safe=True)

    """ 
        删除用户
    """

    def delete(self, request):
        data = QueryDict(request.body).dict()
        pk = data.get('id')
        try:
            self.model.objects.filter(pk=pk).delete()
            res = {'code': 0, 'result': '删除用户成功'}
        except:
            logger.error("delete user  error: %s" % traceback.format_exc())
            res = {'code': 1, 'errmsg': '删除用户失败'}
        return JsonResponse(res, safe=True)


class UserDetailView(LoginRequiredMixin, DetailView):
        '''
            用户详情
        '''

        model = UserProfile
        template_name = "dashboard/user_edit.html"
        context_object_name = "user"

        '''
            更新用户信息
        '''
        def post(self, request, **kwargs):
            pk = kwargs.get("pk")
            data = QueryDict(request.body).dict()
            try:
                self.model.objects.filter(pk=pk).update(**data)
                res = {'code': 0, "next_url": "/dashboard/userlist/", 'result': '更新用户成功'}
            except:
                res = {'code': 1, "next_url": "/dashboard/userlist/", 'errmsg': '更新用户失败'}
                logger.error("update user  error: %s" % traceback.format_exc())
            return render(request, settings.JUMP_PAGE, res)


class ModifyPwdView(LoginRequiredMixin, View):
    """
        重置密码
    """
    @method_decorator(permission_required('dashboard',login_url='/'))
    def get(self, request):
        uid = request.GET.get('uid', None)
        return render(request, 'dashboard/change_passwd.html', {'uid': uid})

    def post(self, request):
        uid = request.POST.get('uid', None)
        pwd1 = request.POST.get("password1", "")
        pwd2 = request.POST.get("password2", "")
        if pwd1 != pwd2:
            return render(request, "dashboard/change_passwd.html", {"msg": "两次密码不一致，你可长点儿心吧！"})

        try:
            user = UserProfile.objects.get(pk=uid)
            user.password = make_password(pwd1)
            user.save()

            # 修改用户的gitlab密码
            '''
            gitlab_user = gl.users.list(username=user.username)[0]
            gitlab_user.password = pwd2
            gitlab_user.save()
            '''
            return HttpResponseRedirect(reverse('index'))
        except:
            logger.error("change_passwd error: %s" % traceback.format_exc())
            return render(request, "dashboard/change_passwd.html", {"msg": "密码修改失败"})


class UserGroupPowerView(LoginRequiredMixin, DetailView):
    '''
        更新用户信息
    '''
    template_name = 'dashboard/user_group_power.html'
    model = UserProfile
    context_object_name = 'user'

    # 返回所有组，并将当前用户所拥有的组显示
    def get_context_data(self, **kwargs):
        context = super(UserGroupPowerView, self).get_context_data(**kwargs)
        context['user_has_groups'], context['user_has_permissions'] = self.get_user_group()
        context['user_not_groups'], context['user_not_permissions'] = self.get_user_not_group()
        return context

    # 获取当前用户所有组，以列表形式返回
    def get_user_group(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            user = self.model.objects.get(pk=pk)
            return user.groups.all(), user.user_permissions.all()
        except self.model.DoesNotExist:
            raise Http404

    # 获取当前用户没有的组，以列表形式返回
    def get_user_not_group(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            user = self.model.objects.get(pk=pk)
            all_group = Group.objects.all()
            groups = [group for group in all_group if group not in user.groups.all()]
            all_perms = Permission.objects.all()
            perms = [perm for perm in all_perms if perm not in user.user_permissions.all()]
            return groups, perms
        except:
            return JsonResponse([], safe=False)

    def post(self, request, *args, **kwargs):
        group_id_list = request.POST.getlist('groups_selected', [])
        permission_id_list = request.POST.getlist('perms_selected', [])
        pk = kwargs.get("pk")
        try:
            user = self.model.objects.get(pk=pk)
            user.groups = group_id_list
            user.user_permissions = permission_id_list
            res = {'code': 0, 'next_url': '/dashboard/userlist/', 'result': '用户角色权限更新成功'}
        except:
            res = {'code': 1, 'next_url': '/dashboard/userlist/', 'errmsg': '用户角色权限更新失败'}
            logger.error("edit  user group pwoer error: %s" % traceback.format_exc())
        return render(request, settings.JUMP_PAGE, res)






>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5

