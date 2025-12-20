from django.test import TestCase
from .models import Product
import datetime
from django.utils import timezone
from django.urls import reverse


def create_product(product_name, days):
    """
    Create a product with the given 'product_name', 'product_type', given number of `days` offset to now (negative for products added
    in the past, positive for products that have yet to be added) and 'amount'.
    """
    time = timezone.now() - datetime.timedelta(days=days)
    return Product.objects.create(product_name=product_name, created_at=time)

class ProductModelTests(TestCase):
    def test_was_bought_recently_with_old_product(self):
        """
        was_bought_recently() returns False for products whose entry_date is older than 2 days
        """
        time = timezone.now() - datetime.timedelta(days=2, hours=23, minutes=59, seconds=59)
        product = Product(product_name="Banana", created_at = time)
        self.assertFalse(product.was_bought_recently())

    def test_was_bought_recently_with_recent_product(self):
        """
        was_bought_recently() returns True for products whose entry_date is within last 2 days
        """
        time = timezone.now() - datetime.timedelta(days=1, hours=23, minutes=59, seconds=59)
        product = Product(product_name="Banana", created_at = time)
        self.assertTrue(product.was_bought_recently())

class ProductIndexViewTests(TestCase):
    def test_no_products(self):
        """
        If no products exist, an appropriate message is displayed
        """
        response = self.client.get(reverse("tracker:products"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(response.context["product_list"], [])
