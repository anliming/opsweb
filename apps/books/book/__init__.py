# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from books.models import Publish, Author, Book
from books.forms import BookForm
# Create your views here.

class BookListView(LoginRequiredMixin,ListView,PaginationMixin):
    template_name = 'books/book_list.html'
    model = Book
    context_object_name = 'book_list'
    paginate_by = 5
    keyword=''

    def get_queryset(self):
        queryset = super(BookListView,self).get_queryset()
        self.keyword = self.request.GET.get('keyword','').strip()
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains=self.keyword)|
                                       Q(authors__name__icontains=self.keyword) |
                                       Q(publisher__name__icontains=self.keyword))
        return queryset
    def get_context_data(self, **kwargs):
        context = super(BookListView,self).get_context_data(**kwargs)
        context['authors']=Author.objects.all()
        context['publishs']=Publish.objects.all()
        context['keyword'] = self.keyword
        return context
    def post(self,request):
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            res = {'code': 0, 'result': '添加图书成功'}
        else:
            # form.errors会把验证不通过的信息以对象的形式传到前端，前端直接渲染即可
            res = {'code': 1, 'errmsg': form.errors}
        return JsonResponse(res, safe=True)
class BookDetailView(DetailView):
    template_name = 'books/book_detail.html'
    model = Book
    context_object_name = 'book'
    next_url='/books/booklist/'
    def get_context_data(self,**kwargs):
        context = super(BookDetailView,self).get_context_data(**kwargs)
        context['authors'] = self.object.authors.all()
        context['publishs'] = Publish.objects.all()
        return context

    def post(self,request,*args,**kwargs):
        pk = kwargs.get('pk')
        p = self.model.objects.get(pk=pk)
        form = BookForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            res = {"code": 0, "result": "更新书籍成功", 'next_url': self.next_url}
        else:
            res = {"code": 1, "errmsg": form.errors, 'next_url': self.next_url}
        return render(request,settings.JUMP_PAGE,res)

    def delete(self,request,*args,**kwargs):
        pk = kwargs.get('pk')
        try:
            obj = self.model.objects.get(pk=pk)
            if obj:
                obj.delete()
                res = {"code": 0, "result": "删除书籍成功"}
            else:
                res = {"code": 1, "errmsg": "书籍不存在,请联系管理员"}
        except Exception as e :
            res = {"code": 2, "errmsg":e.message}
        return JsonResponse(res, safe=True)
class BookAddView(LoginRequiredMixin,ListView):
    template_name = 'books/book_add.html'
    model = Book
    next_url = '/books/booklist/'
    def get_context_data(self, **kwargs):
        context = super(BookAddView,self).get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['publishs'] = Publish.objects.all()
        return context
    def post(self, request, *args, **kwargs):
        form = BookForm(request.POST)
        r_btn = request.POST.get('_save')
        if form.is_valid():
            form.save()
            if r_btn:
                res = {"code": 0, "result": "添加书籍成功", 'next_url': self.next_url}
            else:
                self.next_url='/books/bookadd/'
                res = {"code": 0, "result": "添加书籍成功", 'next_url': self.next_url}
        else:
            res = {"code": 1, "result": "添加书籍失败", 'next_url': self.next_url}
        return render(request,settings.JUMP_PAGE,res)