# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect
from django.views.generic import View, TemplateView, ListView, DetailView,CreateView, UpdateView

from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from pure_pagination.mixins import PaginationMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.files.base import ContentFile


from .models import Tasks, ExecResult
from .forms import TaskAddForm,TaskAdd1Form
from utils.ansible_api import AnsiblePlaybookAPI
import logging, traceback,json

logger = logging.getLogger("opsweb")


class TaskAdd1View(LoginRequiredMixin, CreateView):
    template_name = 'tasks/task_add1.html'
    model = Tasks
    form_class = TaskAdd1Form

    def get_success_url(self):
        return reverse('task:list')

    def form_valid(self, form):
        playbook_text = form.cleaned_data['playbook_text']
        form.instance.playbook.save(form.cleaned_data['name'] + '.yml', ContentFile(playbook_text))
        return super(TaskAdd1View, self).form_valid(form)


class TaskEditView(LoginRequiredMixin, UpdateView):
    template_name = 'tasks/task-edit.html'
    model = Tasks
    context_object_name = "task"
    form_class = TaskAdd1Form

    def get_success_url(self):
        return reverse('task:list')

    def form_valid(self, form):
        playbook_text = form.cleaned_data['playbook_text']
        self.object.playbook.delete()
        form.instance.playbook.save(form.cleaned_data['name'] + '.yml', ContentFile(playbook_text))
        return super(TaskEditView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TaskEditView, self).get_context_data(**kwargs)
        playbook_text = ''
        with open(self.object.playbook.path, 'r') as f:
            for line in f:
                playbook_text += line
        context['playbook_text'] = json.dumps(playbook_text)
        return context


class TaskAddView(LoginRequiredMixin,TemplateView ):
    # def get(self, request):
    #     forms = TaskAddForm()
    #     return render(request, 'tasks/task_add.html', {'forms': forms})

    template_name = "tasks/task_add.html"

    def post(self, request):
        forms = TaskAddForm(request.POST, request.FILES)
        if forms.is_valid():
            forms.save()
            '''
            name = forms.cleaned_data['name']
            playbook = forms.cleaned_data['playbook']
            auto_task = Tasks()
            auto_task.name = name
            auto_task.playbook = playbook
            auto_task.save()
            '''
            return HttpResponseRedirect(reverse('task:list'))
        else:
            return render(request, 'tasks/task_add.html', {'forms': forms, 'errmsg': '表单验证不通过'})


class TaskListView(LoginRequiredMixin, PaginationMixin, ListView):
    """
        任务列表
    """
    model = Tasks
    template_name = 'tasks/tasks_list.html'
    context_object_name = "tasklist"
    paginate_by = 5
    keyword = ''

    def get_queryset(self):
        queryset = super(TaskListView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '')
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword)|
                                        Q(detail_result__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

    """
        playbook执行
    """

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('task_id', 0)
        task = Tasks.objects.get(pk=int(pk))
        print "path is %s " % task.playbook.path
        try:
            playbook = AnsiblePlaybookAPI(task.playbook.path)
            exec_result = playbook.run()
            task.detail_result = exec_result['detail']
            task.status = 'Y'
            task.save()
        except:
            logger.error("insert Tasks  error: %s" % traceback.format_exc())
            return HttpResponse(json.dumps({'status': 1,'msg': '任务执行失败'}),
                            			content_type="application/json")


        simple = exec_result['simple']
        for record in simple:
            try:
                task_result = ExecResult()
                task_result.task = task
                task_result.host = record
                task_result.unreachable = simple[record]['unreachable']
                task_result.skipped = simple[record]['skipped']
                task_result.ok = simple[record]['ok']
                task_result.changed = simple[record]['changed']
                task_result.failures = simple[record]['failures']
                task_result.save()
            except:
                logger.error("insert ExecResult  error: %s" % traceback.format_exc())
                return HttpResponse(json.dumps({'status': 1,'msg': '任务信息获取失败'}),
                            			content_type="application/json")

        return HttpResponse(json.dumps({'status': 0,
                                        'task_status': task.status,
                                        'task_exec_result': simple,
                                        'msg': '任务执行成功'}),
                            content_type="application/json")


class TaskDetailView(LoginRequiredMixin, DetailView):
    '''
         任务详情
    '''
    template_name = 'tasks/task_detail.html'
    model = Tasks
    context_object_name = 'task'


