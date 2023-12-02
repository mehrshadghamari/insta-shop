from django.db import models


class Shop(models.Model):
    owner = models.OneToOneField()
    name = models.CharField(max_length=127)
    end_time = models.DateTimeField()
    phone_number = models.CharField(max_length=127)
    category_work = models.CharField(max_length=127)

