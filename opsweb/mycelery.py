<<<<<<< HEAD
import os
import django
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycelery.settings')

django.setup()

app = Celery('mycelery')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
=======
import os  
import django 
from celery import Celery  
from django.conf import settings
            
# set the default Django settings module for the 'celery' program.  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mycelery.settings')
                        
django.setup()              
                            
app = Celery('mycelery')    
  
app.config_from_object('django.conf:settings')  
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)  
 
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
