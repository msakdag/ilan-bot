import re

import requests
from bs4 import BeautifulSoup

URL = "https://www.ilan.gov.tr/ilan/kategori/44/kamu-personel-alim-ve-sinavlari?currentPage=0"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ilan-bot/0.1)"}

r = requests.get(URL, headers=HEADERS, timeout=30)
print("Durum kodu:", r.status_code, "| Sayfa boyutu:", len(r.text))

soup = BeautifulSoup(r.text, "html.parser")
seen = set()
for a in soup.find_all("a", href=True):
    m = re.match(r"^(?:https://www\.ilan\.gov\.tr)?/ilan/(\d+)/", a["href"])
    if m and m.group(1) not in seen:
        seen.add(m.group(1))
        print(m.group(1), "|", a.get_text(" ", strip=True)[:100], "|", a["href"])
        if len(seen) >= 10:
            break

print("Bulunan ilan sayisi:", len(seen))
