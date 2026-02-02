from tracker.models import ProductDetails, ProductBase

def load_product_details(cleaned_product_details: list[dict]):
    base_not_found_list = []
    to_create = []
    to_update = []

    # 🔥 ONE query instead of thousands
    bases = ProductBase.objects.in_bulk(field_name="reference")

    existing_details = {
        pd.reference_id: pd
        for pd in ProductDetails.objects.all()
    }

    for product in cleaned_product_details:
        reference = product["reference"]
        base = bases.get(reference)

        if not base:
            base_not_found_list.append(product)
            continue

        existing = existing_details.get(reference)

        if existing:
            existing.product_brand = product["product_brand"]
            existing.product_description = product["product_description"]
            to_update.append(existing)
        else:
            to_create.append(
                ProductDetails(
                    reference=base,
                    product_brand=product["product_brand"],
                    product_description=product["product_description"],
                )
            )

    if to_create:
        ProductDetails.objects.bulk_create(to_create, batch_size=500)

    if to_update:
        ProductDetails.objects.bulk_update(
            to_update,
            ["product_brand", "product_description"],
            batch_size=500,
        )

    return to_create + to_update, base_not_found_list
