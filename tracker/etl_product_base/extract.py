from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl

def extract_product_base(feed_url: str) -> list[dict]:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    html = urlopen(feed_url, context=ctx).read()
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.tbody.find_all('tr')

    products_raw = []

    for tag in tags:
        tr_content = tag.find_all("td")
        reference = tr_content[0].string
        ean = tr_content[1].string
        product_name = tr_content[2].string
        details_link = tr_content[3].a.get('href')
        product = {"reference":reference,
                   "ean":ean,
                   "product_name":product_name,
                   "details_link":details_link}
        products_raw.append(product)

    return products_raw