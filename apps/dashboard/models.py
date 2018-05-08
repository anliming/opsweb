# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    name_cn = models.CharField('中文名', max_length=30)
    phone = models.CharField('手机', max_length=11, null=True, blank=True)
    GENDER_CHOICES = (
        ('1', u'总监'),
        ('2', u'经理'),
        ('3', u'研发'),
    )
    role = models.CharField(max_length=4, default='3', choices=GENDER_CHOICES)
    note = models.CharField(max_length=128, default='', blank=True)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.role

    def __unicode__(self):
        return self.username
