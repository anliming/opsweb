# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse,QueryDict,Http404
from django.core.urlresolvers import reverse
from django.views.generic import View, ListView, DetailView
from django.db.models import Q
from django.core.mail import send_mail
import traceback,json,logging
from django.utils.decorators import method_decorator
from  django.contrib.auth.decorators import  permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from pure_pagination.mixins import PaginationMixin


# 自定义模块导入
from .models import WorkOrder
from .forms import WorkOrderApplyForm, WorkOrderResultForm
from django.conf import settings
from .tasks import sendmail


logger = logging.getLogger("opsweb")


class WorkOrderApplyView(LoginRequiredMixin, View):
    def get(self, request):
        forms = WorkOrderApplyForm()
        return render(request, 'order/workorder_apply.html', {'forms': forms})

    def post(self, request):
        forms = WorkOrderApplyForm(request.POST)
        if forms.is_valid():
            '''
            type = request.POST.get('type', '')
            title = request.POST.get('title', '')
            order_contents = request.POST.get('order_contents', '')
            assign_to = request.POST.get('assign_to')
           '''
            print forms.cleaned_data
            type = forms.cleaned_data["type"]
            title = forms.cleaned_data["title"]
            order_contents = forms.cleaned_data["order_contents"]
            assign_to = forms.cleaned_data["assign_to"]


            work_order = WorkOrder()
            work_order.type = int(type)
            work_order.title = title
            work_order.order_contents = order_contents
            work_order.assign_to_id = int(assign_to)
            work_order.applicant = request.user
            work_order.status = 0
            work_order.save()

            # 给指派的人发邮件
            #send_mail(work_order.title,
            #            work_order.order_contents,
            #            settings.EMAIL_FROM,
            #            ['787696331@qq.com',处理人的邮箱],
            #            fail_silently=False,)
            sendmail.delay(work_order.title,
                        work_order.order_contents,
                        settings.EMAIL_FROM,
                        ['787696331@qq.com'],
            )    
            return HttpResponseRedirect(reverse('work_order:list'))

        else:
            return render(request, 'order/workorder_apply.html', {'forms': forms, 'errmsg': '工单填写格式出错！'})


class WorkOrderListView(LoginRequiredMixin, PaginationMixin, ListView):
    '''
        未处理工地列表展示
    '''

    model = WorkOrder
    template_name = 'order/workorder_list.html'
    context_object_name = "orderlist"
    paginate_by = 5
    keyword = ''

    def get_queryset(self):
        queryset = super(WorkOrderListView, self).get_queryset()

        # 只显示状态小于2，即申请和处理中的工单
        queryset = queryset.filter(status__lt=2)

        # 如果不是sa组的用户只显示自己申请的工单，别人看不到你申请的工单，管理员可以看到所有工单
        if 'sa' not in [group.name for group in self.request.user.groups.all()]:
            queryset = queryset.filter(applicant=self.request.user)

        self.keyword = self.request.GET.get('keyword', '')
        if self.keyword:
            queryset = queryset.filter(Q(title__icontains = self.keyword)|
                                       Q(order_contents__icontains = self.keyword)|
                                       Q(result_desc__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WorkOrderListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

    def delete(self, request, *args, **kwargs):
        try:
            data = QueryDict(request.body)
            pk = data.get('id')
            work_order = WorkOrder.objects.get(pk=pk)
            work_order.status = 3
            work_order.save()
            ret = {'code': 0, 'result': '取消工单成功！'}
        except:
            ret = {'code': 1, 'errmsg': '取消工单失败！'}
            logger.error("delete order  error: %s" % traceback.format_exc())
        return JsonResponse(ret, safe=True)


class WorkOrderDetailView(LoginRequiredMixin, DetailView):
    '''
        工单详情页，包括处理结果表单的填写
    '''

    model = WorkOrder
    template_name = "order/workorder_detail.html"
    context_object_name = "work_order"

    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        work_order = self.model.objects.get(pk=pk)

        if work_order.status == 0:
            work_order.status = 1
            work_order.save()
            return render(request, 'order/workorder_detail.html', {'work_order': work_order,
                                                                    'msg': '您已经接受工单！'})
        if work_order.status == 1:
            forms = WorkOrderResultForm(request.POST)
            if forms.is_valid():
                result_desc = request.POST.get('result_desc', '')
                work_order.result_desc = result_desc
                work_order.status = 2
                work_order.save()
                return HttpResponseRedirect(reverse('work_order:list'))
            else:
                return render(request, 'order/workorder_detail.html', {'work_order': work_order,
                                                                        'errmsg': '必须填写处理结果！'})


class WorkOrderHistoryView(LoginRequiredMixin, PaginationMixin, ListView):
    '''
         历史工单查询
    '''

    model = WorkOrder
    template_name = 'order/workorder_history.html'
    context_object_name = "historylist"
    paginate_by = 5
    keyword = ''

    def get_queryset(self):
        queryset = super(WorkOrderHistoryView, self).get_queryset()

        # 显示所有处理完毕的工作
        queryset = queryset.filter(status__gte=2)

        # 如果不是sa组的用户只显示自己申请的工单，别人看不到你申请的工单，管理员可以看到所有工单
        if 'sa' not in [group.name for group in self.request.user.groups.all()]:
            queryset = queryset.filter(applicant=self.request.user)

        self.keyword = self.request.GET.get('keyword', '')
        if self.keyword:
            queryset = queryset.filter(Q(title__icontains = self.keyword)|
                                       Q(order_contents__icontains = self.keyword)|
                                       Q(result_desc__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(WorkOrderHistoryView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context




