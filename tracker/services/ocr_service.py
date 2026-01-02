# This service takes the image of the receipt,
# extracts and normalizes its data. Outputs a list of
# products and its characteristics

from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import torch
from itertools import batched

def process_receipt(image_file_path : str) -> list[dict]:
    raw = extract_data(image_file_path)
    data = normalize_data(raw)
    return data

def extract_data(image_file_path : str) -> list[dict]:
    # Model creation
    device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    model = ocr_predictor(pretrained=True).to(device)
    # model result contains a Document object with Pages, Blocks and
    # Lines where the words are that we are interested in
    doc_file = DocumentFile.from_images(image_file_path)
    result = model(doc_file)
    lines = result.pages[0].blocks[0].lines
    # this will tell us where the product section begins once
    # start_product_section = True and end once end_product_section = True
    start_product_section = False
    end_production_section = False

    products_messy = []
    for line in lines:
        # Store products and their info from each line
        # Access each word in the line
        product_line = []
        for word in line.words:
            if word.value == "FISKALNY": 
                start_product_section = True
            elif word.value == "SPRZEDAZ":
                end_production_section = True
                break
            elif start_product_section:
                product_line.append(word.value)
        if len(product_line) >= 1:
            products_messy.append(product_line)
        if end_production_section:
            break
    # Pair product names, codes with quantity and price 
    product_batches = list(batched(products_messy, 2))
    # Create a dict for each product with its values and store in a list
    products = []
    for batch in product_batches:
        product = {
                "code" : batch[0][-1],
                "quantity" : batch[1][0].split("x")[0],
                "price" : batch[1][-1],
                        }
        products.append(product)
    return products

def normalize_data(products : list[dict]) -> list[dict]:
    for product in products:
        product["code"] = product["code"][:-1]
        product["quantity"] = float((product["quantity"]).replace(",", "."))
        product["price"] = float(product["price"].replace(",", ".")[:-1])
    return products
