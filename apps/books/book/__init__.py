# coding=utf8
from django.views.generic import ListView, DetailView
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionDenied
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import  permission_required

from django.conf import settings
from books.models import Author, Book, Publish
from books.forms import BookForm

import traceback
import logging
logger = logging.getLogger('opsweb')


class BookListView(LoginRequiredMixin, PaginationMixin, ListView):
    '''
        动作：getlist, create
    '''
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "book_list"
    paginate_by = 5
    keyword = ''

    # @method_decorator(permission_required('book.books_admin', login_url='/'))
    def get_queryset(self):
        queryset = super(BookListView, self).get_queryset()
        self.keyword = self.request.GET.get('keyword', '').strip()
        if self.keyword:
            # 跨表搜索
            queryset = queryset.filter(Q(name__icontains = self.keyword)|
                                       Q(authors__name__icontains = self.keyword)|
                                       Q(publisher__name__icontains=self.keyword))
        return queryset

    # @method_decorator(permission_required('book.books_admin', login_url='/'))
    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        context['keyword'] = self.keyword
        context['authors'] = Author.objects.all()
        context['publishs'] = Publish.objects.all()
        return context

    @method_decorator(permission_required('book.books_admin', login_url='/'))
    def post(self, request):
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            res = {'code':0,'result': '添加书成功'}
            logger.info("%s 新填加书成功" % request.user)
        else:
            res = {'code': 1,'errmsg': form.errors}
            logger.error("errmsg %s " % form.errors)
        return JsonResponse(res, safe=True)


class BookDetailView(LoginRequiredMixin, DetailView):
    '''
        动作：getone, update, delete
    '''
    model = Book
    template_name = "books/book1_detail.html"
    context_object_name = 'book'
    next_url = '/books/booklist/'

    def get_context_data(self, **kwargs):
        context = super(BookDetailView, self).get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['publishs'] = Publish.objects.all()
        context['author_list'] = self.get_book_authors()
        return context

    def get_book_authors(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        book = self.model.objects.get(pk=pk)
        author_list = ["%s" % author.id for author in book.authors.all()]
        print author_list
        return author_list

    @method_decorator(permission_required('book.books_admin', login_url='/'))
    def post(self, request, **kwargs):
        pk = kwargs.get('pk')
        a = self.model.objects.get(pk=pk)
        form = BookForm(request.POST, instance=a)
        if form.is_valid():
            form.save()
            res = {"code": 0, "result": "更新书成功", 'next_url': self.next_url}
        else:    
            res = {"code": 1, "errmsg": form.errors, 'next_url': self.next_url}
            print "error: %s" % form.errors
        # 中间页方案
        return render(request,settings.JUMP_PAGE,res)
        # return HttpResponseRedirect(reverse('books:book_detail',args=[pk]))

    @method_decorator(permission_required('book.books_admin', login_url='/'))
    def delete(self, **kwargs):
        pk = kwargs.get('pk')
        try:
            self.model.objects.filter(pk=pk).delete()
            res = {"code": 0, "result": "删除图书成功"}
        except:
            res = {"code": 1, "errmsg": "删除错误请联系管理员"}
            logger.error("delete book  error: %s" % traceback.format_exc())
        return JsonResponse(res, safe=True)

