from tracker.etl_product_details.extract import extract_product_details
from tracker.etl_product_details.transform import transform_product_details
from tracker.etl_product_details.load import load_product_details
from django.core.management.base import BaseCommand
import time

class Command(BaseCommand):
    help = "Run ProductDetails ETL pipeline. Data is scraped from Auchan site"
    def handle(self, *args, **options):
        # Extraction
        extract_start = time.time()
        extract_dict = extract_product_details()
        extract_end = time.time()
        extract_time = str(extract_end - extract_start)
        self.stdout.write(f"Product Details extracted in, {extract_time} seconds.")

        # Transformation
        transform_start = time.time()
        transformed_dict = transform_product_details(extract_dict)
        transform_end = time.time()
        transform_time = str(transform_end - transform_start)
        self.stdout.write(f"Product Details transformed in, {transform_time} seconds.")

        # Load
        load_end = time.time()
        new_product_details, base_not_found_list = load_product_details(transformed_dict)
        load_start = time.time()
        load_time = str(load_end - load_start)
        self.stdout.write(f"Product Details loaded in, {load_time} seconds.")
        
        for base_not_found_detail in base_not_found_list:
            self.stdout.write(f"This product has not been found: {base_not_found_detail}")
            
        self.stdout.write(f"{len(new_product_details)} were added.")
        self.stdout.write(f"{len(base_not_found_list)} were not found.")
        self.stdout.write(self.style.SUCCESS("ProductDetails imported."))