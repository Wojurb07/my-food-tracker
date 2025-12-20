from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import ssl
import regex as re

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\p{L}\s]", " ", text)
    text = re.sub(r"\b\p{L}{1,2}\b", " ", text)  # remove short words
    text = re.sub(r"\s+", " ", text).strip()
    return text

df = pd.read_csv('product_base.csv')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Find div with class "card", "desc", "info", "info-2", "row"

#    Div class = "info" or class = "info-2":
#       Div class="row" THEN <strong> == column name and " ..." is content

urls = df['Dane Produktowe'].to_list()
dicts = []

for url in urls:
    product_dict = dict()
    html = urlopen(url, context=ctx).read()
    ref = url.split("/")[-1]
    soup = BeautifulSoup(html, "html.parser")
    row_tags = soup('div', class_ = "row")
    table = soup.find_all("td")
    product_dict["Referencja"] = ref
    # print("tags: ", row_tags)
    # print("table: ", table)
    for tag in row_tags:
        # print(tag.text)
        strings = tag.text.split(":")
        column = strings[0]
        content = strings[1]
        product_dict[column.strip().lower()] = content

    for index, row in enumerate(table):
        if index > 1 and index % 2 == 0:
            product_dict[clean_text(row.text)] = table[index + 1].text
        else:
            continue

    # print("product_dict: ", product_dict)
    dicts.append(product_dict)

product_details_df = pd.DataFrame(dicts)
# print("final dicts", dicts)
product_details_df.to_csv("product_details.csv")