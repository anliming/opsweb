# _*_ coding: utf-8 _*_
from django.shortcuts import render
from django.views.generic import View, TemplateView,  ListView
from pure_pagination import Paginator, PageNotAnInteger
from utils.gitlab_utils import gl, get_user_projects


# 自定义模块
from .forms import ProjectAddForm
from django.contrib.auth.mixins import LoginRequiredMixin


class ProjectListView(LoginRequiredMixin, ListView):
    """
    登陆用户所有项目列表
    """

    def get(self, request):
        my_projects = get_user_projects(request)
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(my_projects, 10, request=request)
        projects = p.page(page)
        return render(request, 'projects/project_list.html', {'page_obj': projects, 'p': p})


class ProjectAddView(LoginRequiredMixin, TemplateView):
    """
    添加项目
    """
    template_name = 'projects/project_add.html'

    def post(self, request):
        forms = ProjectAddForm(request.POST)
        if forms.is_valid():
            # url = request.POST.get('url', '')
            group = request.POST.get('group', 0)
            print(group)
            name = request.POST.get('name', '')
            description = request.POST.get('description', '')
            visibility_level = request.POST.get('visibility_level', '')

            # 因为gitlab中的group和运维平台中的group同名，但不同id,故要通过传过来的group name找到gitlab中对应的group id
            group_id = gl.groups.search(group)[0].id
            print(group_id)
            project = gl.projects.create({'name': name,
                                          'namespace_id': group_id,
                                          'description': description,
                                          'visibility_level': visibility_level})

            if project:
                return render(request, 'projects/project_add.html', {'msg': '添加{0}成功！'.format(name)})
            else:
                return render(request, 'projects/project_add.html', {'forms': forms, 'msg': project})
        else:
            return render(request, 'projects/project_add.html', {'forms': forms, 'msg': '添加项目失败。格式不正确！'})


