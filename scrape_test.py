import re

import requests
import urllib3
from playwright.sync_api import sync_playwright

urllib3.disable_warnings()

print("--- iskur robots.txt ---")
try:
    rb = requests.get("https://www.iskur.gov.tr/robots.txt", timeout=30, verify=False)
    print(rb.status_code)
    print(rb.text[:400])
except Exception as e:
    print("HATA", str(e)[:80])

SAYFALAR = [
    ("ILAN", "https://www.ilan.gov.tr/ilan/kategori/44/kamu-personel-alim-ve-sinavlari"),
    ("ISKUR-MEMUR", "https://www.iskur.gov.tr/ilanlar/kamu-memur-alim-ilanlari"),
    ("ISKUR-ISCI", "https://www.iskur.gov.tr/ilanlar/kurumdisi-kamu-isci-alim-ilanlari/"),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(ignore_https_errors=True, locale="tr-TR")
    for ad, url in SAYFALAR:
        print("=====", ad)
        page = context.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
        except Exception as e:
            print("Yukleme uyarisi:", str(e)[:80])
        links = page.eval_on_selector_all(
            "a[href]",
            "els => els.map(e => [e.innerText.trim().slice(0, 90), e.getAttribute('href')])",
        )
        ilan = [l for l in links if re.search(r"/ilan/\d+/", l[1]) or ".pdf" in l[1].lower()]
        print("toplam baglanti:", len(links), "| ilan benzeri:", len(ilan))
        for metin, href in ilan[:8]:
            print(" -", metin.replace("\n", " "), "|", href[:100])
        if not ilan:
            govde = page.inner_text("body")
            print("Sayfa metni (ilk 300):", govde[:300].replace("\n", " "))
        page.close()
    browser.close()
    
