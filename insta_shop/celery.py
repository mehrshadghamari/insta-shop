import os

from celery import Celery

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "insta_shop.settings"
)  # Replace 'proj.settings' with your settings module

app = Celery("insta-shop")
app.config_from_object("django.conf:settings", namespace="CELERY")
# app.autodiscover_tasks()
# Manually specify task modules
app.conf.update(
    include=[
        "apps.shop.tasks",
    ]
)
