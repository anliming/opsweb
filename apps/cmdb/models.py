# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from dashboard.models import UserProfile


class Product(models.Model):
    name = models.CharField("业务线名称", max_length=32)
    pid = models.ForeignKey("self", null=True, blank=True, verbose_name="上级业务线")
    module_letter = models.CharField("字母简称", max_length=32)
    op_interface = models.ManyToManyField(UserProfile, verbose_name='运维负责人', related_name='op')
    dev_interface = models.ManyToManyField(UserProfile, verbose_name='业务负责人', related_name='dev')

    def __str__(self):
        return "{}".format(self.module_letter)


class Host(models.Model):
    STATUS = (
        ('Running', '运行中'),
        ('Starting', '启动中'),
        ('Stopping', '停止中'),
        ('Stopped', '已停止')
    )
    CHARGE_TYPE = (
        ('PrePaid', '预付费'),
        ('PostPaid', '后付费')
    )
    CLOUD = (
        ('aliyun', '阿里云'),
        ('qcloud', '腾讯云')
    )

    cloud_type = models.CharField(max_length=20, choices=CLOUD, default='aliyun', verbose_name='云主机类型')
    instance_id = models.CharField(max_length=22, unique=True, verbose_name='实例ID')
    instance_name = models.CharField(max_length=22, verbose_name='实例的显示名称')
    description = models.CharField(max_length=128, null=True, blank=True, verbose_name='实例的描述')
    image_id = models.CharField(max_length=50, verbose_name='镜像ID')
    region_id = models.CharField(max_length=30, verbose_name='实例所属地域ID')
    zone_id = models.CharField(max_length=30, verbose_name='实例所属可用区')
    cpu = models.IntegerField(verbose_name='CPU核数')
    memory = models.IntegerField(verbose_name='内存大小，单位: GB')
    instance_type = models.CharField(max_length=30, verbose_name='实例资源规格')
    status = models.CharField(max_length=8, choices=STATUS, default='Running', verbose_name='实例状态')
    hostname = models.CharField(max_length=23, blank=True, null=True, verbose_name='实例机器名称')
    public_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='公网IP')
    private_ip = models.GenericIPAddressField(verbose_name='私网IP')
    os_type = models.CharField(max_length=10, default='linux', verbose_name='操作系统类型')
    os_name = models.CharField(max_length=20, default='', verbose_name='操作系统名称')
    instance_charge_type = models.CharField(max_length=8, default='PrePaid', choices=CHARGE_TYPE, verbose_name='实例的付费方式')
    creation_time = models.DateTimeField(verbose_name='创建时间')
    expired_time = models.DateTimeField(verbose_name='过期时间')
    business_line = models.ManyToManyField('Product', blank=True, verbose_name='业务线')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='入库时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '主机'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.instance_name


class Disk(models.Model):
    """
        磁盘信息
    """
    DEVICE_TYPE = (
        ('system', '系统盘'),
        ('data', '数据盘')
    )

    host = models.ForeignKey('Host', verbose_name='主机')
    disk_id = models.CharField(max_length=22, null=True, blank=True, verbose_name='磁盘ID')
    device = models.CharField(max_length=15, null=True, blank=True, verbose_name='所属Instance的Device信息')
    size = models.IntegerField(verbose_name='磁盘大小，单位GB')
    type = models.CharField(default='data', max_length=6, choices=DEVICE_TYPE, verbose_name='磁盘类型')
    creation_time = models.DateTimeField(verbose_name='创建时间')
    expired_time = models.DateTimeField(verbose_name='过期时间')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='入库时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '磁盘'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.device


