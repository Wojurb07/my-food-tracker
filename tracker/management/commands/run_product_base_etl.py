from tracker.etl_product_base.extract import extract_product_base
from tracker.etl_product_base.transform import transform_product_base
from tracker.etl_product_base.load import load_product_base
from django.core.management.base import BaseCommand
import time
import datetime

class Command(BaseCommand):
    help = "Run ProductBase ETL pipeline. Data is scraped from Auchan site"
    def handle(self, *args, **options):
        # Extraction
        extract_start = time.time()
        raw_data = extract_product_base("https://apps.auchan.pl/feed/getCard/feed")
        extract_end = time.time()
        extract_time = str(extract_end - extract_start)
        self.stdout.write(f"Product Base extracted in, {extract_time} seconds.")
        
        # Transformation
        transform_start = time.time()
        cleaned_data, invalid_products = transform_product_base(raw_data)
        transform_end = time.time()
        transform_time = str(transform_end - transform_start)
        self.stdout.write(f"Product Base transformed in, {transform_time} seconds.")
        for product in invalid_products:
            self.stdout.write(f"Invalid product data: {product}")
        
        # Load
        load_start = time.time()
        new_products, updated_products = load_product_base(cleaned_data)
        load_end = time.time()
        load_time = str(load_end - load_start)
        self.stdout.write(f"Product Base loaded in, {load_time} seconds.")

        # Final logs
        for new_product in new_products:
            self.stdout.write(f"New product added: {new_product}")
        for updated_product in updated_products:
            self.stdout.write(f"This product has been updated: {updated_product}")

        self.stdout.write(f"{len(updated_products)} were updated.")
        self.stdout.write(f"{len(new_products)} were added.")
        self.stdout.write(self.style.SUCCESS("ProductBase imported."))