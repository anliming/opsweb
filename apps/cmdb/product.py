# coding:utf8
from django.views.generic import  View, TemplateView, ListView, DetailView
from django.shortcuts import render
from django.core.urlresolvers import reverse
from cmdb.models import Product
from dashboard.models import UserProfile
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import  ProductForm

from cmdb.forms import ProductForm
from django.conf import settings

import json
import logging
logger = logging.getLogger('opsweb')

class ProductAddView(LoginRequiredMixin, TemplateView):
    template_name = "cmdb/product_add.html"

    def get_context_data(self, **kwargs):
        context = super(ProductAddView, self).get_context_data(**kwargs)
        context['user_object_list'] = UserProfile.objects.all()
        context['products'] = Product.objects.filter(pid_id=None)
        return context

    def post(self, request):
        res = {"code": 0, 'next_url': reverse("cmdb:host_list")}
        form = ProductForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                res['result'] = "添加业务线成功"
            except Exception as e:
                msg = "用户{} 业务线出错：{}".format(request.user.username, e.args)
                logger.error(msg)
                res['code'] = 1
                res['errmsg'] = msg

        else:
            msg = "用户{} 添加业务线验证失败:{}".format(request.user.username, form.errors)
            logger.error(msg)
            res['code'] = 1
            res['errmsg'] = msg
        return render(request, settings.JUMP_PAGE, res)
class Ztree(object):
    # 初始化获取所有产品线信息
    def __init__(self):
        self.data = Product.objects.all()

    # 内部函数，遍历一级产品线
    def _get_one_product(self):
        return [p for p in self.data if p.pid_id == None]

    # 内部函数，传入一级业务线ID，并遍历其二级产品线
    def _get_second_product(self, pid):
        return [p for p in self.data if p.pid_id == pid]

    # 将所有一级业务线及其所属的二级业务线格式化输出，生成树状结构
    def get(self):
        ret = []
        url = "/cmdb/product_detail/"
        for one_obj in self._get_one_product():
            tmp = {}
            tmp['pid'] = 0
            tmp['id'] = one_obj.id
            tmp['name'] = one_obj.name
            tmp['url'] = url+str(one_obj.id)
            tmp['open'] = 'true'
            tmp['children'] = []
            for child in self._get_second_product(one_obj.id):
                childrens = {"pid": one_obj.id, "name": child.name, "id": child.id, "url": url+str(child.id)}
                tmp['children'].append(childrens)
            ret.append(tmp)
        return ret


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "cmdb/product_manage.html"
    context_object_name = "product"
    next_url = '/cmdb/product_detail'

    '''
        展示业务线信息
    '''

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['user_list'] = UserProfile.objects.all()
        context['ztree'] = json.dumps(Ztree().get())
        context['parent_nodes'] = Product.objects.filter(pid_id=None)
        context['dev_list'], context['op_list'] = self.get_product_user()
        context['host_list'] = self.get_product_host()
        return context

    def get_product_user(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        p = self.model.objects.get(pk=pk)
        dev_list = ["%s" % dev.id for dev in p.dev_interface.all()]
        op_list = ["%s" % op.id for op in p.op_interface.all()]
        return dev_list, op_list

    def get_product_host(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        p = self.model.objects.get(pk=pk)
        host_list = p.host_set.all()
        return host_list


    def post(self,request,*args,**kwargs):

        pk = kwargs.get('pk')
        p = self.model.objects.get(pk=pk)
        form = ProductForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            res = {"code": 0,"result": "更新产品线成功", 'next_url': reverse("cmdb:product_detail", args=[1])}
        else:
            res = {"code": 1, "errmsg": form.errors, 'next_url': reverse("cmdb:product_detail", args=[1])}
        return render(request, settings.JUMP_PAGE, res)


