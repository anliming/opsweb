# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class Tasks(models.Model):
    name = models.CharField(max_length=128, verbose_name=u'任务名称')
    playbook = models.FileField(upload_to='playbook/%Y/%m', verbose_name=u'playbook文件')
    detail_result = models.TextField(verbose_name=u'执行结果详情')
    status = models.CharField(max_length=1, choices=(('Y', '已执行'), ('N', '未执行')), default='N', verbose_name='执行状态')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=u'任务创建时间')
    exec_time = models.DateTimeField(auto_now=True, verbose_name=u'执行时间')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u'add_task'
        verbose_name_plural = verbose_name
        ordering = ['-add_time']


class ExecResult(models.Model):
    task = models.ForeignKey(Tasks, verbose_name=u'任务')
    host = models.CharField(max_length=64, verbose_name=u'主机名')
    unreachable = models.IntegerField(verbose_name=u'不可达')
    skipped = models.IntegerField(verbose_name=u'跳过')
    ok = models.IntegerField(verbose_name=u'成功')
    changed = models.IntegerField(verbose_name=u'改变')
    failures = models.IntegerField(verbose_name=u'失败')

    def __unicode__(self):
        return self.task.name

    class Meta:
        verbose_name = u'task_result'
        verbose_name_plural = verbose_name