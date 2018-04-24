# _*_ coding: utf-8 _*_
from __future__ import unicode_literals
from django.db import models
from dashboard.models import UserProfile
<<<<<<< HEAD
import datetime
=======

>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5

class WorkOrder(models.Model):
    ORDER_TYPE = (
        (0, '数据库'),
        (1, 'WEB服务'),
        (2, '计划任务'),
        (3, '配置文件'),
        (4, '其它'),
    )
    STATUS = (
        (0, '申请'),
        (1, '处理中'),
        (2, '完成'),
        (3, '失败'),
    )
    title = models.CharField(max_length=100, verbose_name=u'工单标题')
    type = models.IntegerField(choices=ORDER_TYPE, default=0, verbose_name=u'工单类型')
    order_contents = models.TextField(verbose_name='工单内容')
    applicant = models.ForeignKey(UserProfile, verbose_name=u'申请人', related_name='work_order_applicant')
    assign_to = models.ForeignKey(UserProfile, verbose_name=u'指派给')
    status = models.IntegerField(choices=STATUS, default=0, verbose_name=u'工单状态')
    result_desc = models.TextField(verbose_name=u'处理结果', blank=True, null=True)
    apply_time = models.DateTimeField(auto_now_add=True, verbose_name=u'申请时间')
    complete_time = models.DateTimeField(auto_now=True, verbose_name=u'处理完成时间')

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = 'work_order'
        verbose_name_plural = verbose_name
        ordering = ['-complete_time']

<<<<<<< HEAD
class  OrderStatistics(models.Model):
     uid = models.ForeignKey(UserProfile, verbose_name=u'用户名')
     type0 = models.IntegerField(default=0, verbose_name=u'工单类型_数据库')
     type1 = models.IntegerField(default=0, verbose_name=u'工单类型_WEB服务')
     type2 = models.IntegerField(default=0, verbose_name=u'工单类型_计划任务')
     type3 = models.IntegerField(default=0, verbose_name=u'工单类型_配置文件')
     type4 = models.IntegerField(default=0, verbose_name=u'工单类型_其他')
     statime = models.DateField(default=(datetime.date.today() - datetime.timedelta(days=1)), verbose_name=u'处理完成时间')
=======
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
