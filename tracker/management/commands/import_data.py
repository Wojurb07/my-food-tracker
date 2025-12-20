import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from tracker.models import ProductBase, ProductDetails

class Command(BaseCommand):
    help = "Import cleaned product data for ProductBase and ProductDetails. Data was scaped from Auchan site and cleaned in Jupyter Notebook"

    def handle(self, *args, **options):

        base_df = pd.read_csv("auchan-data/product_base_cleaned.csv", encoding='utf-8')

        for _, row in base_df.iterrows():
            ProductBase.objects.update_or_create(
                reference=row["Referencja"],      
                    defaults={                       
                    "ean": row["EAN"],
                    "product_name": row["Nazwa"],
                    "details_link": row["Dane Produktowe"],
        }
        )
            self.stdout.write(f"Importing reference {row['Referencja']}")        
        self.stdout.write(self.style.SUCCESS("ProductBase imported"))

        details_df = pd.read_csv("auchan-data/product_details_cleaned.csv", encoding='utf-8')

        for _, row in details_df.iterrows():
            try:
                base = ProductBase.objects.get(reference=row["Referencja"])
            except ProductBase.DoesNotExist:
                continue

            ProductDetails.objects.update_or_create(
                reference=base,        
                defaults={
                    "product_brand": row["marka"],
                    "product_weight": row["waga"],
                    "product_measurement": row["jednostka opisowa"],
                    "calories": row["wartość energetyczna"],
                    "fats": row["tłuszcz"],
                    "carbohydrates": row["węglowodany"],
                    "sugar": row["cukry"],
                    "protein": row["białko"],
                    "salt": row["sól"],
                    "category": row["kategoria"]
                }
            )
            self.stdout.write(f"Importing reference {row['Referencja']}")
        self.stdout.write(self.style.SUCCESS("ProductDetails imported"))