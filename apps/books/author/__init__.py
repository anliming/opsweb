# coding=utf8
<<<<<<< HEAD
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from django.conf import settings
from books.models import Publish, Author, Book
from books.forms import AuthorForm

import json
import logging

logger = logging.getLogger('opsweb')


class AuthorListView(LoginRequiredMixin,ListView,PaginationMixin):
    template_name = 'books/author_list.html'
    model = Author
    context_object_name = 'author_list'
    paginate_by = 5
    keyword=''

    def get_queryset(self):
        queryset = super(AuthorListView,self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword) |
                                       Q(address__icontains=self.keyword)|
                                       Q(email__icontains=self.keyword))
        return queryset
    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        return context
    def post(self,request):
=======
from django.views.generic  import  ListView, DetailView
from django.db.models import Q
from django.http  import JsonResponse,HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import permission_required
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.conf import settings
from books.models import Author, Book
from books.forms import AuthorForm

import traceback
import logging
logger = logging.getLogger('opsweb')


class AuthorListView(LoginRequiredMixin,PermissionRequiredMixin, PaginationMixin, ListView):
    '''
        动作：getlist, create
    '''
    model = Author
    template_name = "books/author_list.html"
    context_object_name = "author_list"
    paginate_by = 5
    keyword = ''
    permission_required = ('books.book_admin',)

    def get_queryset(self):
        queryset = super(AuthorListView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains = self.keyword)|
                                       Q(address__icontains = self.keyword)|
                                       Q(email__icontains=self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        context['books'] = Book.objects.all()
        return context

    # @method_decorator(permission_required('books.book_admin', login_url='/'))
    # def get(self, request, *args, **kwargs):
    #     return super(AuthorListView, self).get(request, *args, **kwargs)

    # @method_decorator(permission_required('books.book_admin', login_url='/'))
    def post(self, request):
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            res = {'code': 0, 'result': '添加作者成功'}
        else:
<<<<<<< HEAD
            # form.errors会把验证不通过的信息以对象的形式传到前端，前端直接渲染即可
            res = {'code': 1, 'errmsg': form.errors}
        return JsonResponse(res, safe=True)

class AuthorDetailView(LoginRequiredMixin,DetailView):
    template_name = 'books/author_detail.html'
    model = Author
    context_object_name = 'author'
    next_url = '/books/authorlist/'
    def post(self,request,*args,**kwargs):
        pk = kwargs.get('pk')
        p = self.model.objects.get(pk=pk)
        form = AuthorForm(request.POST,instance=p)
        if form.is_valid():
            form.save()
            res = {"code": 0, "result": "更新作者成功", 'next_url': self.next_url}
        else:
            res = {"code": 1, "errmsg": form.errors, 'next_url': self.next_url}
        return render(request, settings.JUMP_PAGE, res)

    def delete(self,*args,**kwargs):
        pk=kwargs.get('pk')
        obj = self.model.objects.get(pk=pk)
        try:
            if obj.book_set.all():
                res = {"code": 1, "errmsg": "该作者有关联书籍,请联系管理员"}
            else:
                obj.delete()
                res = {"code": 0, "errmsg": "删除成功"}
        except Exception as e:
            res = {"code": 2, "errmsg": e.message}
        return JsonResponse(res, safe=True)
=======
            res = {'code': 1, 'errmsg': form.errors}
        return JsonResponse(res, safe=True)


class AuthorDetailView(LoginRequiredMixin,DetailView):
    '''
        动作：getone, update, delete
    '''
    model = Author
    template_name = "books/author_detail.html"
    context_object_name = 'author'
    next_url = '/books/authorlist/'

    def post(self, request, **kwargs):
        pk = kwargs.get('pk')
        a = self.model.objects.get(pk=pk)
        form = AuthorForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            res = {"code": 0, "result": "更新作者成功", 'next_url': self.next_url}
        else:    
            res = {"code": 1, "errmsg": form.errors, 'next_url': self.next_url}
        return render(request, settings.JUMP_PAGE, res)
        # return HttpResponseRedirect(reverse('books:author_detail',args=[pk]))
 
    def delete(self, **kwargs):
        pk = kwargs.get('pk')
        # 通过出版社对象查所在该出版社的书籍，如果有关联书籍不可以删除，没有关联书籍可以删除
        try:
            obj = self.model.objects.get(pk=pk)
            if not obj.book_set.all():
                self.model.objects.filter(pk=pk).delete()
                res = {"code": 0, "result": "删除作者成功"}
            else:
                res = {"code": 1, "errmsg": "该作者有关联书籍,请联系管理员"}
        except:
            res = {"code": 1, "errmsg": "删除错误请联系管理员"}
            logger.error("delete author error: %s" % traceback.format_exc())
        return JsonResponse(res, safe=True)

>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
