import re

from playwright.sync_api import sync_playwright

LISTE = "https://www.ilan.gov.tr/ilan/kategori/44/kamu-personel-alim-ve-sinavlari"
ANAHTAR = ["son başvuru", "başvuru tarih", "alınacak", "kontenjan", "yayın", "sınav tarih"]

with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(ignore_https_errors=True, locale="tr-TR")
    s = c.new_page()
    s.goto(LISTE, wait_until="networkidle", timeout=60000)
    linkler = s.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
    ilanlar = []
    for h in linkler:
        if re.search(r"/ilan/\d+/", h) and "kamu-personel-alim-ve-sinavlari" in h and h not in ilanlar:
            ilanlar.append(h)
    print("Ilan sayisi:", len(ilanlar))
    for url in ilanlar[:2]:
        print("=====", url[:110])
        d = c.new_page()
        d.goto(url, wait_until="networkidle", timeout=60000)
        metin = d.inner_text("body")
        print("Toplam metin:", len(metin))
        print(metin[:700].replace("\n", " | "))
        print("--- anahtar satirlar ---")
        for satir in metin.split("\n"):
            if any(k in satir.lower() for k in ANAHTAR):
                print(" >", satir.strip()[:150])
        d.close()
    b.close()
    
