import datetime
from django.utils import timezone
from django.db import models

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=200)
    entry_date = models.DateTimeField("Upload date")
    amount = models.FloatField(default=0)

    def was_bought_recently(self):
        return self.entry_date >= (timezone.now() - datetime.timedelta(days=2))

    def __str__(self):
        return self.product_name