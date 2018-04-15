#coding:utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse,QueryDict,Http404
from django.core.urlresolvers import reverse
from django.views.generic import View, ListView, DetailView
from django.db.models import Q
from django.contrib.auth.models import Group, Permission

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# 自定义模块导入

from dashboard.models import UserProfile
from django.conf import settings
from pure_pagination.mixins import PaginationMixin
from dashboard.forms import GroupForm

import traceback,json,logging


logger = logging.getLogger("opsweb")


class GroupListView(LoginRequiredMixin, PermissionRequiredMixin, PaginationMixin, ListView):
    """
        查看组列表、添加组、删除组
    """
    permission_required = ('dashboard.admin',)
    model = Group
    template_name = 'dashboard/group_list.html'
    context_object_name = "grouplist"
    paginate_by = 5
    keyword = ''

    def get_queryset(self):
        queryset = super(GroupListView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '')
        if self.keyword:
            queryset = queryset.filter(name__icontains = self.keyword)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(GroupListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

    """
        添加组
    """

    def post(self, request):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            ret = {'code': 0, 'result': '添加组成功'}
        else:
            ret = {'code': 1, 'errmsg': '添加组失败'}
        return JsonResponse(ret, safe=True)

    """
       删除组
    """

    def delete(self, request):
        data = QueryDict(request.body)
        pk = data.get('id',None)
        try:
            group_obj = self.model.objects.get(pk=pk)
            if group_obj.user_set.all():
                res = {'code': 1, 'errmsg': '删除权限失败,组里有成员无法删除'}
            else:
                self.model.objects.filter(pk=pk).delete()
                res = {'code': 0, 'result': '删除组成功'}
        except:
            res = {'code': 1, 'errmsg': '更新组失败'}
            logger.error("delete group  error: %s" % traceback.format_exc())
        return JsonResponse(res, safe=True)


class GroupDetailView(LoginRequiredMixin, DetailView):
    """
    编辑小组权限
    """
    model = Group
    template_name = 'dashboard/group_edit.html'
    context_object_name = "group"
    pk_url_kwarg = 'pk'

    # 返回所有权限，并将当前组所拥有的权限选中
    def get_context_data(self, **kwargs):
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        context['group_has_permissions'] = self.get_group_permission()
        context['group_not_permissions'] = self.get_group_not_permission()
        return context

    # 获取当前组所有权限，以列表形式返回
    def get_group_permission(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            group = Group.objects.get(pk=pk)
            return group.permissions.all()
        except Group.DoesNotExist:
            raise Http404

    # 获取当前组没有的权限，以列表形式返回
    def get_group_not_permission(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        try:
            group = Group.objects.get(pk=pk)
            all_perms = Permission.objects.all()
            perms = [perm for perm in all_perms if perm not in group.permissions.all()]
            print perms
            return perms
        except:
            return JsonResponse([], safe=False)

    # 更新组的权限
    def post(self, request,*args, **kwargs):
        permission_id_list = request.POST.getlist('perms_selected', [])
        gid = request.POST.get('gid')
        name = request.POST.get('name')
        try:
            group = self.model.objects.get(pk=gid)
            group.permissions = permission_id_list
            group.name = name
            group.save()
            res = {'code': 0, 'next_url': '/dashboard/grouplist/', 'result': '组更新成功'}
        except:
            res = {'code': 1, 'next_url': '/dashboard/grouplist/', 'errmsg': '组更新失败'}
            logger.error("edit  group  error: %s" % traceback.format_exc())
        return render(request, settings.JUMP_PAGE, res)


class GroupUsersView(LoginRequiredMixin, View):
    '''
        取出指定组下的所有用户信息
    '''
    def get(self, request):
        gid = request.GET.get('gid', None)
        try:
            group = Group.objects.get(pk=gid)
        except:
            return JsonResponse([], safe=False)
        users = group.user_set.all()
        user_list = [{'username': user.username, 'name_cn': user.name_cn, 'email':user.email, 'id': user.id} for user in users]
        return JsonResponse(user_list, safe=False)

    '''
        将用户从用户组中删除
    '''
    def delete(self, request):
        ret = {'code': 0}
        data = QueryDict(request.body)
        uid = data.get('userid', None)
        gid = data.get('groupid', None)

        try:
            user = UserProfile.objects.get(pk=uid)
            group = Group.objects.get(pk=gid)
            group.user_set.remove(user)
        except UserProfile.DoesNotExist:
            ret['code'] = 1
            ret['errmsg'] = '用户不存在'
        except Group.DoesNotExist:
            ret['code'] = 2
            ret['errmsg'] = '用户组不存在'
        except Exception as e:
            ret['code'] = 3
            ret['errmsg'] = e.args
        return JsonResponse(ret, safe=True)


