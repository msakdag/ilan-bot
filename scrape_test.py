import re

from playwright.sync_api import sync_playwright

import detay

LISTE = "https://www.ilan.gov.tr/ilan/kategori/44/kamu-personel-alim-ve-sinavlari"
AY = "ocak|şubat|mart|nisan|mayıs|haziran|temmuz|ağustos|eylül|ekim|kasım|aralık"
TARIH = re.compile(r"\d{1,2}[\s./]+(?:\d{1,2}|%s)[\s./]+\d{4}" % AY, re.I)

with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(ignore_https_errors=True, locale="tr-TR")
    s = c.new_page()
    s.goto(LISTE, wait_until="networkidle", timeout=60000)
    linkler = s.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
    b.close()

urller = []
for h in linkler:
    if re.search(r"/ilan/\d+/", h) and "kamu-personel-alim-ve-sinavlari" in h and h not in urller:
        urller.append(h)
urller = urller[:10]
metinler = detay.detay_getir(urller)

for url in urller:
    metin = metinler.get(url, "")
    t = detay.tarih_bul(metin)
    print("=====", url.split("/")[4], url[-45:], "| bulunan:", t)
    if t is None:
        n = 0
        for satir in metin.split("\n"):
            if "başvuru" in satir.lower() and TARIH.search(satir):
                print("  >", satir.strip()[:160])
                n += 1
                if n >= 4:
                    break
        print("  tarihli basvuru satiri:", n)
