from tracker.models import ProductBase

def load_product_base(cleaned_product_base: list[dict]):
    
    new_products = []
    updated_products = []

    for product in cleaned_product_base:
        try:
            obj = ProductBase.objects.get(reference = product['reference'])
            if not (obj.ean == product['ean'] and
                    obj.product_name == product['product_name'] and
                    obj.details_link == product['details_link']):
                
                obj.ean = product['ean']
                obj.product_name = product['product_name']
                obj.details_link = product['details_link']
                updated_products.append(obj)
                obj.save()
        except ProductBase.DoesNotExist:
            obj = ProductBase.objects.create(reference = product['reference'],
                                            ean = product['ean'],
                                            product_name = product['product_name'],
                                            details_link = product['details_link'])
            new_products.append(obj)
    return new_products, updated_products