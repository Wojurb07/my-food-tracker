from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://apps.auchan.pl/feed/getCard/feed"
html = urlopen(url, context=ctx).read()
soup = BeautifulSoup(html, "html.parser")
tags = soup('a')

data = pd.read_html(html)
df = data[0]

df['Referencja'] = df['Referencja'].apply(str)
df['EAN'] = df['EAN'].apply(str)

for tag in tags:
    ref = tag.get('href', None).split('/')[-1]
    df['Dane Produktowe'][df['Referencja']==ref] = tag.get('href', None)
    
df.to_csv("product_base.csv")