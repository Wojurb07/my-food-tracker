import datetime
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class ProductBase(models.Model):
    reference = models.CharField('Referencja', max_length=8, unique=True)
    ean = models.CharField('EAN', max_length=13)
    product_name = models.CharField("Nazwa", max_length=200)
    details_link = models.URLField("Dane Produkowe", max_length=300)
    
class ProductDetails(models.Model):
    reference = models.OneToOneField(ProductBase, on_delete=models.CASCADE, to_field='reference', primary_key=True)
    product_brand = models.CharField('marka', max_length=200, null=True, blank=True)
    product_weight = models.FloatField('waga', validators=[MinValueValidator(0)], null=True, blank=True)
    product_measurement = models.CharField('jednostka opisowa', max_length=5, null=True, blank=True)
    calories = models.FloatField('wartość energetyczna', null=True, blank=True)
    fats = models.FloatField('tłuszcz', null=True, blank=True)
    carbohydrates = models.FloatField('węglowodany', null=True, blank=True)
    sugar = models.FloatField('cukry', null=True, blank=True)
    protein = models.FloatField('białko', null=True, blank=True)
    salt = models.FloatField('sól', null=True, blank=True)
    category = models.CharField('kategoria', max_length=10, null=True, blank=True)

class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    reference = models.ForeignKey(ProductBase, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def was_bought_recently(self):
        return self.created_at >= (timezone.now() - datetime.timedelta(days=2))

    def __str__(self):
        return self.product_name