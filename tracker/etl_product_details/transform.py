from bs4 import BeautifulSoup
import regex as re

def extract_brand(row_tags):
    for tag in row_tags:
        text = tag.get_text(separator=" ", strip=True)

        normalized = clean_text(text)

        if normalized.startswith("marka standaryzowana"):
            return text.split(":", 1)[1].strip()

        if normalized.startswith("marka"):
            return text.split(":", 1)[1].strip()
    return None

def extract_desc(row_tags):
    cleaned_texts = []

    for row in row_tags:
        for strong in row.find_all("strong"):
            strong.decompose()

        text = row.get_text(separator=" ", strip=True)

        if text:
            cleaned_texts.append(text)

    return " ".join(cleaned_texts)

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\p{L}\s]", " ", text)
    text = re.sub(r"\b\p{L}{1,2}\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def transform_product_details(extracted_dict: list[dict]) -> list[dict]:

    product_details = []

    for product_html in extracted_dict:
        soup = BeautifulSoup(product_html['html'], "html.parser")

        row_tags_for_brand = soup.find_all("div", class_="row")
        product_brand = extract_brand(row_tags_for_brand)

        row_tags_for_desc = soup.find_all("div", class_="row")
        product_description = extract_desc(row_tags_for_desc)
        product_details.append({'reference' : product_html['reference'],
                               'product_brand' : product_brand,
                               'product_description' : product_description,
                               "scraped_at" : product_html['scraped_at']})
    return product_details