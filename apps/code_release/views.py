# -*- coding: utf-8 -*-

import os
import json, logging, traceback

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.views.generic import View, TemplateView, ListView, DetailView
from pure_pagination.mixins import PaginationMixin
from django.db.models import Q


# 自定义模块
from .forms import ApplyForm, DeployForm
from .models import Deploy
from dashboard.models import UserProfile
from utils.gitlab_utils import gl, get_user_projects
from django.contrib.auth.mixins import LoginRequiredMixin

logger = logging.getLogger("opsweb")


class GetProjectVersionsView(LoginRequiredMixin, View):
    """
    获取指定项目的所有版本
    """

    def get(self, request):
        project_id = request.GET.get('project_id', '').split('/')[0]
        print project_id
        tags = gl.project_tags.list(project_id=int(project_id))
        tags = [[tag.name, tag.message] for tag in tags]
        return HttpResponse(json.dumps(tags), content_type='application/json')


class ApplyView(LoginRequiredMixin, TemplateView):
    """
    申请发布
    """

    template_name = 'deploy/apply.html'

    def get_context_data(self, **kwargs):
        context = super(ApplyView, self).get_context_data(**kwargs)
        context['user_projects'] = get_user_projects(self.request)
        context['assign_to_users'] = UserProfile.objects.filter(groups__name='sa')
        return context

    def post(self, request):
        forms = ApplyForm(request.POST)
        if forms.is_valid():
            name = request.POST.get('name', '')
            project_version = request.POST.get('project_version', '')
            version_desc = request.POST.get('version_desc', '')
            assigned_to = request.POST.get('assigned_to', '')
            update_detail = request.POST.get('update_detail', '')

            has_apply = Deploy.objects.filter(name=name.split('/')[1], status__lt=2)
            if has_apply:
                return render(request, 'deploy/apply.html',
                              {'errmsg': '该项目已经申请上线，但是上线还没有完成，上线完成后方可再次申请！'})
            try:
                apply_release = Deploy()
                apply_release.name = name.split('/')[1]
                apply_release.project_version = project_version
                apply_release.version_desc = version_desc
                apply_release.assigned_to_id = assigned_to
                apply_release.update_detail = update_detail
                apply_release.status = 0
                apply_release.applicant_id = request.user.id
                apply_release.save()
                return HttpResponseRedirect(reverse('deploy:apply_list'))
            except:
                logger.error("apply the release error: %s" % traceback.format_exc())
                return render(request, 'deploy/apply.html',{'errmsg':'申请失败，请查看日志'})
        else:
            print(forms.errors)
            return render(request, 'deploy/apply.html', {'forms': forms, 'errmsg': '申请格式错误！'})


class ApplyListView(LoginRequiredMixin,PaginationMixin,ListView):
    """
    申请发布列表
    """

    model = Deploy
    template_name = "deploy/apply_list.html"
    context_object_name = "apply_list"
    paginate_by = 5
    keyword = ''

    def get_queryset(self):
        queryset = super(ApplyListView, self).get_queryset()
        queryset = queryset.filter(status__lt=2)
        print queryset
        self.keyword = self.request.GET.get('keyword', '')
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword) |
                                           Q(update_detail__icontains=self.keyword) |
                                           Q(version_desc__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ApplyListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

    def post(self, request):
        try:
            apply_id = request.POST.get('apply_id', '')
            Deploy.objects.filter(id=int(apply_id)).update(status=3)
            ret = {'code':0,'result':"取消上线成功！"}
        except:
            logger.error("Cancel the release error: %s" % traceback.format_exc())
            ret = {'code':1,'errmsg':"取消上线失败！"}

        return JsonResponse(ret, safe=True)


class DeployView(LoginRequiredMixin, DetailView):
    """
    通过获取当前项目状态，执行代码发布功能
    """

    model = Deploy
    template_name = 'deploy/deploy.html'
    context_object_name = 'deploy'

    def get_context_data(self, **kwargs):
        context = super(DeployView, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        forms = DeployForm(request.POST)
        if forms.is_valid():
            pk = kwargs.get('pk')
            deploy = Deploy.objects.get(pk=pk)
            if deploy:
                # 如果status为0,说明是申请状态，点击了仿真按钮，需要上线到仿真环境，并把status改为1
                if deploy.status == 0:
                    deploy.status = 1
                    # 通过Jenkins api 操作将制定项目的代码推送到规定的服务器上去
                    msg = "灰度发布完成"
                # 如果状态为1 ，说明已经是仿真状态，点击上线按钮，讲代码推到正式环境，同时状态改为2
                elif deploy.status == 1:
                    deploy.status = 2
                    # 通过Jenkins api 操作将制定项目的代码推送到规定的服务器上去
                    msg = "正式发布完成"
                else:
                    return HttpResponseRedirect(reverse('deploy:deploy_history'))
                deploy.save()
                return render(request, 'deploy/deploy.html', {'deploy': deploy, 'msg': msg})
        else:
            return render(request, 'deploy/deploy.html', {'errmsg': "提交格式不正确", 'forms': forms})


class DeployHistoryView(LoginRequiredMixin, PaginationMixin, ListView):
    """
    获取所有上线完成/失败的项目记录
    """

    model = Deploy
    template_name = "deploy/deploy_history.html"
    context_object_name = "deploy_history"
    paginate_by = 10
    keyword = ''

    def get_queryset(self):
        queryset = super(DeployHistoryView, self).get_queryset()
        queryset = queryset.filter(status__gte=2).order_by('-deploy_time')
        # 管理员能看到所有历史，个人只能看到自己的发布历史

        self.keyword = self.request.GET.get('keyword', '')
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword) |
                                           Q(update_detail__icontains=self.keyword) |
                                           Q(version_desc__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(DeployHistoryView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context
