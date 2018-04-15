#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse,QueryDict,Http404
from django.core.urlresolvers import reverse
from django.views.generic import View, ListView, DetailView
from django.db.models import Q
from django.contrib.auth.models import Permission,ContentType


from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import  permission_required
from django.contrib.auth.mixins import LoginRequiredMixin

# 自定义模块导入

from django.conf import settings
from pure_pagination.mixins import PaginationMixin
from dashboard.forms import PermForm,PermUpdateForm

import traceback,json,logging


logger = logging.getLogger("opsweb")


class PowerListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
        查看所有用户:只有指定权限的用户可看
    """
    model = Permission
    template_name = 'dashboard/power_list.html'
    context_object_name = "powerlist"
    paginate_by = 5
    keyword = ''


    # @method_decorator(permission_required('dashboard', login_url='/'))
    def get_queryset(self):
        queryset = super(PowerListView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '')
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains = self.keyword)|
                                        Q(codename__icontains = self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PowerListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        context['contents'] = ContentType.objects.all()
        return context

    """
        权限添加
        获取参数及传入代码有待优化
    """
    def post(self, request):
        #name = request.POST.get('name', '')
        #codename = request.POST.get('codename', '')
        #content_type = request.POST.get('content_type', '')
        #res = self.model.objects.create(name=name, codename=codename, content_type_id=content_type)
        form = PermForm(request.POST)
        if form.is_valid():
            form.save()
            ret = {'code': 0, 'result': '添加权限成功'}
        else:
            ret = {'code': 1, 'errmsg': form.errors}
            print form.errors
        return JsonResponse(ret, safe=True)

    """
       删除权限
    """
    def delete(self, request, **kwargs):
        data = QueryDict(request.body)
        pk = data.get('id')
        # 判断权限是否有调用，如果有调用则不允许删除
        try:
            perm = self.model.objects.get(pk=pk)
            if perm.group_set.all() or perm.user_set.all():
                res = {'code': 1, 'errmsg': '删除权限失败.权限已经被调用'}
            else:
                self.model.objects.filter(pk=pk).delete()
                res = {'code': 0, 'result': '删除权限成功'}
        except:
            res = {'code': 1, 'errmsg': '更新权限失败'}
            logger.error("delete power  error: %s" % traceback.format_exc())
        return JsonResponse(res, safe=True)


class PowerDetailView(LoginRequiredMixin, DetailView):
    '''
        用户详情
    '''

    model = Permission
    template_name = "dashboard/power_edit.html"
    context_object_name = "power"

    '''
        更新权限信息
    '''

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        p = self.model.objects.get(pk=pk)
        form = PermUpdateForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            res = {"code": 0, 'next_url': '/dashboard/powerlist/', 'result': '权限更新成功'}
        else:
            res = {"code": 1, 'next_url': '/dashboard/powerlist/', 'errmsg':form.errors}

        return render(request, settings.JUMP_PAGE, res)






