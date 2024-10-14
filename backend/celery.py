import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE",'backend.settings')
app = Celery('backend')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks()


#Restart workers after processing 100 tasks
app.conf.worker_max_tasks_per_child = 100
app.conf.worker_concurrency = 2
app.conf.task_result_expires = 3600
app.conf.task_soft_time_limit = 300
app.conf.task_time_limit = 600
app.conf.task_acks_late = True
