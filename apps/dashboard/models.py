# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    name_cn = models.CharField('中文名', max_length=30)
    phone = models.CharField('手机', max_length=11, null=True, blank=True)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

<<<<<<< HEAD
    def __unicode__(self):
        return self.username
=======
        def __unicode__(self):
            return self.username


class Test(models.Model):
    name = models.CharField('中文名', max_length=30)

    class Meta:
        verbose_name = '测试'
        verbose_name_plural = verbose_name
        permissions = (
            ("test_online", "Can test online "),
            ("apply_online", "Can apply online "),
            ("gray_online", "Can gray online "),
            ("final_online", "Can final online "),
            ("online_history", "Can see history "),
        )

    def __unicode__(self):
        return self.name
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
