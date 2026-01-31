import copy

def is_reference_name_valid(product: dict) -> bool:
    return product['reference'] not in ["", " "] and product['product_name'] not in ["", " "]

def is_reference_ean_valid(product: dict) -> bool:
    return len(product['reference']) <= 6 and 8 <= len(product['ean']) <= 13

def transform_product_base(raw_product_base: list[dict]) -> tuple[list[dict], list[dict]]:
    
    products = copy.deepcopy(raw_product_base)

    products_clean = []
    products_invalid = []

    for product in products:
        for key in product:
            if product[key] and product[key] is not None:
                product[key] = str(product[key])
            elif product[key] == "" or product[key] == " ":
                product[key] = None
        if is_reference_name_valid(product) and is_reference_ean_valid(product):
            products_clean.append(product)
        else:
            products_invalid.append(product)

    return products_clean, products_invalid