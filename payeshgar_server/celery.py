from __future__ import absolute_import, unicode_literals

import os
from kombu import Exchange, Queue
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payeshgar_server.settings')
app = Celery('celery_app')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

#
app.conf.task_queues = (
    Queue(
        'new_result',
        Exchange('new_result'),
        routing_key='new_result',
        queue_arguments={'x-max-priority': 1}
    )
)

app.conf.task_routes = {
    'inspecting.tasks.process_results': {'queue': 'new_result'},
}
