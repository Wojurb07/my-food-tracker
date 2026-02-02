import datetime
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

# Product knowledge base scrapped
class ProductBase(models.Model):
    reference = models.CharField('Referencja', max_length=8, unique=True)
    ean = models.CharField('EAN', max_length=13)
    product_name = models.CharField("Nazwa", max_length=100000)
    details_link = models.URLField("Dane Produkowe", max_length=300)
    
    class Meta:
        ordering = ["product_name"]

    def __str__(self):
        return self.product_name
        
# Product details scrapped from Auchan side
class ProductDetails(models.Model):
    reference = models.OneToOneField(ProductBase, on_delete=models.CASCADE, to_field='reference', primary_key=True)
    product_brand = models.CharField('marka', max_length=100000, null=True)
    product_description = models.CharField('marka', max_length=100000, null=True)

# Product added by the user and stored in the fridge 
class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reference = models.ForeignKey(ProductBase, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def was_bought_recently(self):
        return self.created_at >= (timezone.now() - datetime.timedelta(days=2))

    def __str__(self):
        return self.reference.product_name
    
# Image of the receipt model
class ReceiptImage(models.Model):
    image = models.ImageField(upload_to="receipt_images/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt Image from {self.created_at}"