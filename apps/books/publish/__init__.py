# coding=utf8
<<<<<<< HEAD
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
=======
from django.views.generic  import  ListView, DetailView
from django.db.models import Q
from django.http  import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse 
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from django.conf import settings
<<<<<<< HEAD
from books.models import Publish, Author, Book
from books.forms import PublishForm

import json
import logging

=======
from books.models import Publish
from books.forms import PublishForm

import traceback
import logging
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
logger = logging.getLogger('opsweb')


class PublishListView(LoginRequiredMixin, PaginationMixin, ListView):
    '''
<<<<<<< HEAD
    动作：getlist, create
=======
        动作：getlist, create
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
    '''
    model = Publish
    template_name = "books/publish_list.html"
    context_object_name = "publish_list"
    paginate_by = 5
    keyword = ''

    def get_queryset(self):
        queryset = super(PublishListView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
<<<<<<< HEAD
            queryset = queryset.filter(Q(name__icontains=self.keyword) |
                                       Q(address__icontains=self.keyword) |
=======
            queryset = queryset.filter(Q(name__icontains = self.keyword)|
                                       Q(address__icontains = self.keyword)|
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
                                       Q(city__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PublishListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context

    def post(self, request):
        form = PublishForm(request.POST)
        if form.is_valid():
            form.save()
            res = {'code': 0, 'result': '添加出版商成功'}
        else:
            # form.errors会把验证不通过的信息以对象的形式传到前端，前端直接渲染即可
            res = {'code': 1, 'errmsg': form.errors}
<<<<<<< HEAD
=======
            print form.errors   
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
        return JsonResponse(res, safe=True)


class PublishDetailView(LoginRequiredMixin, DetailView):
    '''
<<<<<<< HEAD
    动作：getone, update, delete
=======
        动作：getone, update, delete
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
    '''
    model = Publish
    template_name = "books/publish_detail.html"
    context_object_name = 'publish'
    next_url = '/books/publishlist/'

<<<<<<< HEAD
    def post(self, request, *args, **kwargs):
=======
    def post(self, request, **kwargs):
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
        pk = kwargs.get('pk')
        p = self.model.objects.get(pk=pk)
        form = PublishForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            res = {"code": 0, "result": "更新出版商成功", 'next_url': self.next_url}
<<<<<<< HEAD
        else:
            res = {"code": 1, "errmsg": form.errors, 'next_url': self.next_url}
        return render(request, settings.JUMP_PAGE, res)
        # return HttpResponseRedirect(reverse('books:publish_detail',args=[pk]))

    def delete(self, request, *args, **kwargs):
=======
        else:    
            res = {"code": 1, "errmsg": form.errors, 'next_url': self.next_url}
        return render(request, settings.JUMP_PAGE, res)
        # return HttpResponseRedirect(reverse('books:publish_detail',args=[pk]))
 
    def delete(self, **kwargs):
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
        pk = kwargs.get('pk')
        # 通过出版社对象查所在该出版社的书籍，如果有关联书籍不可以删除，没有关联书籍可以删除
        try:
            obj = self.model.objects.get(pk=pk)
            if not obj.book_set.all():
                self.model.objects.filter(pk=pk).delete()
                res = {"code": 0, "result": "删除出版商成功"}
            else:
                res = {"code": 1, "errmsg": "该出版社有关联书籍,请联系管理员"}
        except:
            res = {"code": 1, "errmsg": "删除错误请联系管理员"}
<<<<<<< HEAD
=======
            logger.error("delete pushlish error: %s" % traceback.format_exc())
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
        return JsonResponse(res, safe=True)

