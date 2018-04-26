#coding=utf-8
from __future__ import unicode_literals

from django.db import models
# from django.contrib.auth.models import User
from dashboard.models import UserProfile
# Create your models here.

class Basemodel(models.Model):
    '''
       基础表(抽象类)
    '''
    name = models.CharField(max_length=32, verbose_name='名字')
    createtime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updatetime = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    note = models.TextField(default='', null=True, blank=True, verbose_name='备注')

    def __unicode__(self):
        return self.name  # 显示对象的名字

    class Meta:
        abstract = True  # 抽象类
        ordering = ['-id']  # 按id倒排

class InceptSql(Basemodel):
    SQL_STATUS = (
                        (-3, u'已回滚'),
                        (-2, u'已暂停'),
                        (-1, u'待执行'),
                        (0, u'已执行'),
                        (1, u'已放弃'),
                        (2, u'执行失败'),
    )

    ENV = (
        (1, u'生产环境'),
        (2, u'测试环境')
    )

    sqlusers = models.ManyToManyField(UserProfile)
    commiter = models.CharField(max_length = 20)
    sqlcontent = models.TextField(blank = True, null = True)
    env = models.IntegerField(choices = ENV)
    dbname = models.CharField(max_length = 50)
    treater = models.CharField(max_length = 20)
    status = models.IntegerField(default = -1, choices = SQL_STATUS)
    executerz = models.TextField(default='', null=True, blank=True)
    #exedatetime = models.CharField(max_length = 11)
    exe_affected_rows = models.CharField(max_length = 10)
    roll_affected_rows = models.CharField(max_length = 10)
    rollbackopid = models.TextField(blank = True, null = True)
    rollbackdb = models.CharField(max_length = 100)

class optimize(Basemodel):
    optimizeusers = models.ForeignKey(UserProfile)
    sqlcontent = models.TextField(blank = True, null = True)
    env = models.CharField(max_length = 6)
    dbname = models.CharField(max_length = 50)
    optimizerz = models.TextField(blank = True, null = True)
    note = models.CharField(max_length = 100)

class dbconf(Basemodel):
    GENDER_CHOICES = (
                        (1, u'生产'),
                        (2, u'测试'),
    )
    user = models.CharField(max_length = 128)
    password = models.CharField(max_length = 128)
    host = models.CharField(max_length = 16)
    port = models.CharField(max_length = 5)
    env = models.IntegerField(blank = True, null = True, choices = GENDER_CHOICES)

