# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Publish(models.Model):           
    '''
    出版商
    '''
    name = models.CharField(max_length=30, verbose_name='出版商名称')
    address = models.CharField(max_length=5, verbose_name='出版商地址')
    city = models.CharField(max_length=60, verbose_name='出版商城市',  null=True, blank=True)

    class Meta:
        verbose_name = '出版商信息'
        verbose_name_plural = verbose_name
    
    def __unicode__(self):
        return self.name


class Author(models.Model):                     
    '''
    作者
    '''
    name = models.CharField(max_length=40,verbose_name='作者名')
    email = models.EmailField(verbose_name='作者邮箱')
    phone = models.CharField(max_length=11, verbose_name='手机号码', null=True, blank=True)
    address = models.CharField(max_length=128, verbose_name='作者地址',null=True, blank=True)

    class Meta:
        verbose_name = '作者信息'
        verbose_name_plural = verbose_name
    
    def __unicode__(self):
        return self.name


class Book(models.Model):                        
    '''
    图书
    '''
    name = models.CharField("书名", max_length=100)
    # 作者和书是多对多的关系
    authors = models.ManyToManyField(Author, verbose_name="作者")     
    # 一本书只能被一家出版，出版商可以出版多本书
    publisher = models.ForeignKey(Publish, verbose_name="出版社")     
    publication_date = models.DateField("出版时间")

    class Meta:
        verbose_name = '图书信息'
        verbose_name_plural = verbose_name
        ordering = ['-publication_date']  
    
    def __unicode__(self):
        return self.name


