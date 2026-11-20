import re

import requests
import urllib3

urllib3.disable_warnings()
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ilan-bot/0.1)"}


def get(url):
    return requests.get(url, headers=HEADERS, timeout=30, verify=False)


# 1) Gunluk ilan site haritasi
r = get("https://www.ilan.gov.tr/sitemap/daily-ads.xml")
print("daily-ads.xml:", r.status_code, "| boyut:", len(r.text))
print("Ham baslangic:", r.text[:300].replace("\n", " "))

urls = re.findall(r"<loc>(.*?)</loc>", r.text)
print("Toplam adres:", len(urls))
for u in urls[:3]:
    print(" ilk adres:", u)

hedef = [u for u in urls if "kamu-personel-alim-ve-sinavlari" in u]
print("Kamu personel alimi adresleri:", len(hedef))
for u in hedef[:10]:
    print(" -", u)

# 2) Tek bir ilan sayfasi
if hedef:
    d = get(hedef[0])
    print("Ilan sayfasi:", d.status_code, "| boyut:", len(d.text))
    t = re.search(r"<title>(.*?)</title>", d.text, re.S)
    print("Baslik:", t.group(1).strip() if t else "yok")
    
