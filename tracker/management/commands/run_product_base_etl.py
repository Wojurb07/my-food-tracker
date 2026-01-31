from tracker.etl_product_base.extract import extract_product_base
from tracker.etl_product_base.transform import transform_product_base
from tracker.etl_product_base.load import load_product_base
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Run ProductBase ETL pipeline. Data is scraped from Auchan site"
    def handle(self, *args, **options):    
        raw_data = extract_product_base("https://apps.auchan.pl/feed/getCard/feed")
        cleaned_data, invalid_products = transform_product_base(raw_data)
        for product in invalid_products:
            self.stdout.write(f"Invalid product data: {product}")
        new_products, updated_products = load_product_base(cleaned_data)
        for new_product in new_products:
            self.stdout.write(f"New product added: {new_product}")
        for updated_product in updated_products:
            self.stdout.write(f"This product has been updated: {updated_product}")

        self.stdout.write(f"{len(updated_products)} were updated.")
        self.stdout.write(f"{len(new_products)} were added.")
        self.stdout.write(self.style.SUCCESS("ProductBase imported."))