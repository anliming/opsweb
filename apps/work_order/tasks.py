<<<<<<< HEAD
#encoding=utf-8
from opsweb.mycelery import app
from  django.core.mail import send_mail
from  django.conf import settings
import traceback,datetime

from work_order.models import WorkOrder,OrderStatistics
from dashboard.models import UserProfile

@app.task(name="sendmail")
def sendmail(title,order_contents,email_from,email_to):
    try:
        send_mail(title,order_contents,email_from,email_to)
    except:
        print("fail")
        traceback.print_exc()

@app.task(name="testcron")
def testcron():
    send_mail('测试test', "测试celery定时任务",settings.EMAIL_FROM , ["17485252@qq.com",])


@app.task(name="daily_work_order")
def DailyWorkOrder():
    lastday = datetime.date.today()-datetime.timedelta(days=1)
    all_work_order = WorkOrder.objects.filter(apply_time__icontains=lastday)
    #all_work_order = WorkOrder.objects.filter(apply_time__icontains=(datetime.date.today()))
    for user in UserProfile.objects.all():
        user_id = user.id
        if user_id ==1:
            user_order = all_work_order.all()
        else:
            user_order =all_work_order.filter(assign_to_id__exact=user_id)
        order_type0 = user_order.filter(type__exact=0).count()
        order_type1 = user_order.filter(type__exact=1).count()
        order_type2 = user_order.filter(type__exact=2).count()
        order_type3 = user_order.filter(type__exact=3).count()
        order_type4 = user_order.filter(type__exact=4).count()
        print({"user_id":user_id,"type0":order_type0,"type1":order_type1,"type2":order_type2,"type3":order_type3,"type4":order_type4})
        orderstate = OrderStatistics()
        orderstate.statime =  lastday
        orderstate.uid_id = user_id
        if order_type0:
            orderstate.type0 = order_type0
        if order_type1:
            orderstate.type1 = order_type1
        if order_type2:
            orderstate.type2 = order_type2
        if order_type3:
            orderstate.type3 = order_type3
        if order_type4:
            orderstate.type4 = order_type4
        orderstate.save()
         #return {"user_id":user_id,"type0":order_type0,"type1":order_type1,"type2":order_type2,"type3":order_type3,"type4":order_type4}
=======

from opsweb.mycelery import app 
from django.core.mail import send_mail
import traceback,os

@app.task(name="sendmail")
def sendmail(title,order_contents,email_from,email_to):
    try:
    	send_mail(title,order_contents,email_from,email_to)
    except:
        print('fail')
        traceback.print_exc()

@app.task(name="touchfile")
def touchfile():
    os.mkdir("/tmp/aa")
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
