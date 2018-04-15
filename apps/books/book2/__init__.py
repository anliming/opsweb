# coding=utf8
from django.views.generic  import View, TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.http import JsonResponse,HttpResponseRedirect
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from django.conf import settings
from books.models import Author, Book, Publish
from books.forms import PublishForm, AuthorForm, BookForm

import json
import logging
logger = logging.getLogger('opsweb')


class BookAddView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    添加员工
    """
    template_name = 'books/book_add.html'
    model = Book
    fields = ('name', 'authors', 'publisher', 'publication_date')
    success_message = ' Add %(name)s Success'

    def get_success_url(self):
        if '_addanother' in self.request.POST:
            return reverse('books:book_add')
        return reverse('books:book_list')

    def get_context_data(self, **kwargs):
        context = super(BookAddView, self).get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['publishs'] = Publish.objects.all()
        return context


class BookListView(LoginRequiredMixin, PaginationMixin, ListView):
    '''
    动作：getlist, create
    '''
    model = Book
    template_name =  "books/book_list.html"
    context_object_name = "book_list"
    paginate_by = 5
    keyword = ''

    def get_queryset(self):
        queryset = super(BookListView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            queryset = queryset.filter(Q(name__icontains = self.keyword))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        context['authors'] = Author.objects.all()
        context['publishs'] = Publish.objects.all()
        return context

    def post(self, request):
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            res = {'code':0, 'result': '添加书成功'}
        else:
            res = {'code':1, 'errmsg': form.errors}
        return JsonResponse(res,safe=True)


class BookDetailView(LoginRequiredMixin,DetailView):
    '''
    动作：getone, update, delete
    '''
    model = Book
    template_name = "books/book_detail.html"
    context_object_name = 'book'
    next_url = '/books/booklist/'

    def get_context_data(self, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['publishs'] = Publish.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        a = self.model.objects.get(pk=pk)
        form = BookForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            res = {"code":0,"result":"更新书成功", 'next_url':self.next_url}
        else:    
            res = {"code":1,"errmsg":form.errors, 'next_url':self.next_url}
            print "error: %s" % form.errors
            return render(request,settings.JUMP_PAGE,res)
        # return HttpResponseRedirect(reverse('books:book_detail',args=[pk]))
 
    def delete(self, request, *args,  **kwargs):
        pk = kwargs.get('pk')
        try:
            self.model.objects.filter(pk=pk).delete()
            res = {"code":0,"result":"删除图书成功"}
        except:
            res = {"code":1,"errmsg":"删除错误请联系管理员"}
        return JsonResponse(res,safe=True)

