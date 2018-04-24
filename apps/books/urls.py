<<<<<<< HEAD
# coding=utf-8

from django.conf.urls import include, url
from books import publish, author, book

urlpatterns = [
    url(r'^publishlist/$', publish.PublishListView.as_view(), name='publish_list'),
    url(r'^publishdetail/(?P<pk>\d+)?/?$', publish.PublishDetailView.as_view(), name='publish_detail'),

    url(r'^authorlist/$', author.AuthorListView.as_view(), name='author_list'),
    url(r'^authordetail/(?P<pk>\d+)?/?$', author.AuthorDetailView.as_view(), name='author_detail'),
    url(r'^booklist/$', book.BookListView.as_view(), name='book_list'),
    url(r'^bookdetail/(?P<pk>\d+)?/?$', book.BookDetailView.as_view(), name='book_detail'),
    url(r'^bookadd/$', book.BookAddView.as_view(), name='book_add'),
]
=======
#coding=utf-8

from django.conf.urls import include, url
from books import publish, author, book, book2

urlpatterns = [
    url(r'^publishlist/$', publish.PublishListView.as_view(), name='publish_list'),
    url(r'^publishdetail/(?P<pk>\d+)?/?$', publish.PublishDetailView.as_view(), name='publish_detail'),
    
    url(r'^authorlist/$', author.AuthorListView.as_view(), name='author_list'),
    url(r'^authordetail/(?P<pk>\d+)?/?$', author.AuthorDetailView.as_view(), name='author_detail'),
    
    url(r'^booklist/$', book.BookListView.as_view(), name='book_list'),
    url(r'^bookdetail/(?P<pk>\d+)?/?$', book.BookDetailView.as_view(), name='book_detail'),
    url(r'^bookadd/$', book2.BookAddView.as_view(), name='book_add'),
]

>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
