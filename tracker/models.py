import datetime
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Product(models.Model):
    product_name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=200)
    entry_date = models.DateTimeField("Upload date")
    amount = models.FloatField(default=0, validators=[MinValueValidator(0)])
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def was_bought_recently(self):
        return self.entry_date >= (timezone.now() - datetime.timedelta(days=2))

    def __str__(self):
        return self.product_name