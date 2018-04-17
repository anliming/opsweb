# -*- coding: utf-8 -*-
from random import Random # 用于生成随机码
from django.core.mail import send_mail # 发送邮件模块
#from users.models import EmailVerifyRecord # 邮箱验证model
#from MxOnline.settings import EMAIL_FROM  # setting.py添加的的配置信息
#from django.conf.global_settings import EMAIL_FROM
#settings.configure(DEBUG=True)
from django.conf import settings
def send_register_email(email_title,email_body,email_to):
    #email_record = EmailVerifyRecord()
    # 将给用户发的信息保存在数据库中
    #code = random_str(16)
    #email_record.code = code
    #email_record.email = email
    #email_record.send_type = send_type
   # email_record.save()
    # 初始化为空
    email_title = ""
    email_body = ""
    # 如果为注册类型
    #from_email = settings.EMAIL_FROM
#    if send_type == "register":
    email_title = "加入平台通知"
    #email_body = "欢迎加入OPS平台，以下你的账号信息:http://127.0.0.1:8000/active/{0}"
        # 发送邮件
    print(email_title, email_body,settings.EMAIL_FROM,email_to)
    send_status = send_mail(email_title, email_body,settings.EMAIL_FROM,email_to)
    if send_status:
        pass

#send_register_email("drachen@126.com")
