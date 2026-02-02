from urllib.request import urlopen
import ssl
from tracker.models import ProductBase
from datetime import datetime

def extract_product_details() -> list[dict]:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    product_details = []

    for product_base in ProductBase.objects.only("reference", "details_link"):
        url = product_base.details_link
        html = urlopen(url, context=ctx).read()
        scraped_at = datetime.now()

        product = {"reference" : product_base.reference,
                   "html" : html,
                   "scraped_at" : scraped_at,
                   }
        product_details.append(product) 
    
    return product_details