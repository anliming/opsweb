
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
