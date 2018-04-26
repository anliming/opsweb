#coding=utf8
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.db.models import Q

class CkListView(ListView):
    '''
        对 get_queryset, get_context_data, get 方法重写
    '''

    context_object_name = None  # 前端模板变量名'users'，用于模板循环显示
    template_name = None  # 模板名
    ckmodel = None
    paginate_by = 10  # 分页中每一页的记录数目
    pk_url_kwarg = 'pk'
    souword = 'souword'
    orderkey = '-id'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CkListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):  # 数据库查询的结果，对应于context_object_name
        objectsdata = self.ckmodel.objects.all().order_by(self.orderkey)
        souword = self.request.GET.get(self.souword)
        if souword:
            objectsdata = objectsdata.filter(Q(name__contains=souword)|Q(note__contains=souword))  # 模糊搜索匹配souword的（name或note）
        return objectsdata

    def oneobject(self, pk):
        try:                
            oneobject = self.ckmodel.objects.get(pk=pk)
        except self.ckmodel.DoesNotExist:
            data = None
            status = -1  
        else:               
            data = model_to_dict(oneobject)
            status = 0   
        return {'data':data, 'status':status}
                    
    def get_context_data(self, **kwargs):  # 模板变量合集字典
        return super(CkListView, self).get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk:  # 请求单用户数据
            ret = self.oneobject(pk)
            return JsonResponse(ret)
        else:  # 请求所有用户数据（复制的 BaseListView 的get方法）
            self.object_list = self.get_queryset()
            '''
            allow_empty = self.get_allow_empty()

            if not allow_empty:
                # When pagination is enabled and object_list is a queryset,
                # it's better to do a cheap query than to load the unpaginated
                # queryset in memory.
                if (self.get_paginate_by(self.object_list) is not None
                        and hasattr(self.object_list, 'exists')):
                    is_empty = not self.object_list.exists()
                else:
                    is_empty = len(self.object_list) == 0
                if is_empty:
                    raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                            % {'class_name': self.__class__.__name__})
            '''
            context = self.get_context_data()
            return self.render_to_response(context)

