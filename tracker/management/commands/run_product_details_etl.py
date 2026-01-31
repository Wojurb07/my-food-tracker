from tracker.etl_product_details.extract import extract_product_details
from tracker.etl_product_details.transform import transform_product_details
from tracker.etl_product_details.load import load_product_details
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Run ProductDetails ETL pipeline. Data is scraped from Auchan site"
    def handle(self, *args, **options):    
        extract_dict = extract_product_details()
        transformed_dict = transform_product_details(extract_dict)
        new_product_details, base_not_found_list = load_product_details(transformed_dict)

        for new_product_detail in new_product_details:
            self.stdout.write(f"New product details added: {new_product_detail}")
        for base_not_found_detail in base_not_found_list:
            self.stdout.write(f"This product has not been found: {base_not_found_detail}")
            
        self.stdout.write(f"{len(new_product_details)} were added.")
        self.stdout.write(f"{len(base_not_found_list)} were not found.")
        self.stdout.write(self.style.SUCCESS("ProductDetails imported."))