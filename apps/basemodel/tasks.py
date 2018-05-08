#coding=utf-8
# tasks.py
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import time, smtplib
from celery import Celery, platforms
from email.mime.text import MIMEText

platforms.C_FORCE_ROOT = True  # 防止启动报错：C_FORCE_ROOT environment ...
celery = Celery('tasks', broker='redis://127.0.0.1:6379/1')
mail_host = "email.aaa.com"  #设置服务器
mail_user = "user1"    #用户名
mail_pass = "passwd1"   #密码
mail_postfix = "aaa.com"  #发件箱的后缀

@celery.task
def send_mail(to_list, personnel, sqlid, note, mailtype, sqlcontent, dbname):  #to_list：收件人；sub：主题；content：邮件内容
    if mailtype == 'commit':
        title = '提交了 SQL-%s' % sqlid
    elif mailtype == 'execute':
        title = '已执行 SQL-%s' % sqlid
    sqlhtml = ''
    for s in sqlcontent[0:1024].split(';'):
        if s:
            sqlhtml = sqlhtml + '<div>' + s + ';' + '</div>'
    contenthtml = "<span style='margin-right:20px'>%s %s</span> <a href='http://127.0.0.1/sql/sqldetail/?id=%s'>【查看详情】</a> <p>备注：%s</p> <p>数据库（线上环境）：%s </p>" % (personnel, title, sqlid, note, dbname)
    if len(sqlcontent) > 1024:
        sqlhtml = sqlhtml + '<div>' + '略... ...（内容比较多，可查看详情）'  + '</div>'
    #me = "hello"+"<"+mail_user+"@"+mail_postfix+">"   #这里的hello可以任意设置，收到信后，将按照设置显示
    me = "<"+mail_user+"@"+mail_postfix+">"   #这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(contenthtml + sqlhtml, _subtype='html', _charset='utf-8')    #创建一个实例，这里设置为html格式邮件
    msg['Subject'] = '%s %s [%s]' % (personnel, title, note)    #设置主题
    msg['From'] = me
    print '收件人列表: %s' % to_list
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host, 587)  #连接smtp服务器
        s.starttls()
        s.login(mail_user,mail_pass)  #登陆服务器
        s.sendmail(me, to_list, msg.as_string())  #发送邮件
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False

