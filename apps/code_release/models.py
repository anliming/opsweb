# _*_ coding: utf-8 _*_
from __future__ import unicode_literals


from django.db import models
from dashboard.models import UserProfile

# Create your models here.


class Deploy(models.Model):
    STATUS = (
        (0, '申请'),
        (1, '灰度'),
        (2, '上线'),
        (3, '取消上线'),
    )
    name = models.CharField(max_length=40, verbose_name=u'项目名称')
    project_version = models.CharField(max_length=40, verbose_name=u'项目版本')
    version_desc = models.CharField(max_length=100, verbose_name=u'版本描述')
    applicant = models.ForeignKey(UserProfile, verbose_name=u'申请人', related_name="applicant")
    assigned_to = models.ForeignKey(UserProfile, verbose_name=u'指派人', related_name="assigned")
    update_detail = models.TextField(verbose_name=u'更新详情')
    status = models.IntegerField(default=0, choices=STATUS, verbose_name='上线状态')
    apply_time = models.DateTimeField(auto_now_add=True, verbose_name=u'申请时间')
    deploy_time = models.DateTimeField(auto_now=True, verbose_name=u'上线完成时间')