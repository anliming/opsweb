# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseRedirect,JsonResponse
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
<<<<<<< HEAD
from django_otp import match_token, user_has_device, devices_for_user
=======
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5


# 自定义模块导入
from .forms import LoginForm


class LoginView(View):
    """
        登录模块
    """
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        res = {"code": 0}
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get("username", None)
            password = request.POST.get("password", None)
<<<<<<< HEAD
            # token = request.POST.get('token', None)
            user = authenticate(username=username, password=password)
            # mttoken = match_token(user, token)
=======
            user = authenticate(username=username, password=password)
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
            if user is not None:
                if user.is_active:
                    login(request, user)
                    res['next_url'] = '/'
                else:
                    res['code'] = 1
                    res['errmsg'] = '用户被禁用'
            else:
                res['code'] = 1
                res['errmsg'] = '用户名或密码错误'
<<<<<<< HEAD
            # if mttoken is None:# 验证动态码
            #     res['code'] = 1
            #     res['errmsg'] = '动态口令错误'
=======
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
        else:
            res['code'] = 1
            res['errmsg'] = "用户名或密码不能为空"
        return JsonResponse(res, safe=True)


class LogoutView(LoginRequiredMixin,View):
    """
        登出

        关于用户登录验证两种方式：
        1：基于全类所有方法生效的可以利用LoginRequiredMixin
        2：基于类里面某个函数的可以用login_required
    """
    # @method_decorator(login_required)
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse("login"))


class IndexView(View):
    """
        首页
    """
    @method_decorator(login_required(login_url="login"))
    def get(self, request):
<<<<<<< HEAD
        return render(request, 'index.html')
=======
        return render(request, 'index.html')


class TestView(View):
    """
        首页
    """
    @method_decorator(login_required(login_url="login"))
    def get(self, request):
        return render(request, 'dashboard/test.html')
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
