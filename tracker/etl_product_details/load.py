from tracker.models import ProductDetails, ProductBase

def load_product_details(cleaned_product_details: list[dict]):
    
    base_not_found_list = []
    new_product_details = []

    for product in cleaned_product_details:
        try:
            base = ProductBase.objects.get(reference = product['reference'])
        except ProductBase.DoesNotExist:
            base_not_found_list.append(product)
            continue
        
        ProductDetails.objects.update_or_create(
                                    reference=base,
                                    defaults={"product_brand": product["product_brand"],
                                            "product_description": product["product_description"]})
        new_product_details.append(product)
    return new_product_details, base_not_found_list