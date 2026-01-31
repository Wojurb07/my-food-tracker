from fastapi import FastAPI
from tracker.models import ProductBase, ProductDetails

app = FastAPI()

@app.get("/api")
def root():
    return {"status" : "API working"}

@app.get("/api/products/{reference}")
def get_product(reference: int):
    product = ProductBase.objects.get(reference = reference)
    details = ProductDetails.objects.get(reference = product.reference)
    try:
        return {"product_name" : product.product_name, "category" : details.category}
    
    except product.DoesNotExist:
        status_code = 404,
        detail = f"There's no product with {reference} reference."
        return {"status_code":status_code, "detail" : detail}

@app.get("/api/products")
def get_products():
    return list(ProductBase.objects.values("reference", "product_name",))