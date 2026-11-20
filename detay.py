import re
from datetime import date, datetime, timedelta, timezone

from playwright.sync_api import sync_playwright

AYLAR = ["", "ocak", "şubat", "mart", "nisan", "mayıs", "haziran",
         "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık"]
AYLAR_ADI = [a.capitalize() for a in AYLAR]

DESENLER = [
    r"son\s+başvuru\s+(?:tarihi|günü)\s*[:\-]?\s*(?:olan\s+)?(\d{1,2})[\s./]+(\w+)[\s./]+(\d{4})",
    r"(\d{1,2})[\s./]+(\w+)[\s./]+(\d{4})\s+bitiş\s+tarihinde",
]


def bugun():
    return datetime.now(timezone(timedelta(hours=3))).date()


def tarih_yazi(t):
    return "%d %s %d" % (t.day, AYLAR_ADI[t.month], t.year)


def tarih_yap(gun, ay, yil):
    try:
        ay_no = int(ay) if ay.isdigit() else AYLAR.index(ay.lower())
        return date(int(yil), ay_no, int(gun))
    except ValueError:
        return None


def tarih_bul(metin):
    for desen in DESENLER:
        for m in re.finditer(desen, metin, re.IGNORECASE):
            t = tarih_yap(*m.groups())
            if t:
                return t
    return None


def detay_getir(urller):
    sonuc = {}
    with sync_playwright() as p:
        tarayici = p.chromium.launch()
        baglam = tarayici.new_context(ignore_https_errors=True, locale="tr-TR")
        for url in urller:
            sayfa = baglam.new_page()
            try:
                sayfa.goto(url, wait_until="networkidle", timeout=60000)
                sonuc[url] = sayfa.inner_text("body")
            except Exception as e:
                print("Detay okunamadi:", url[-40:], str(e)[:60])
            sayfa.close()
        tarayici.close()
    return sonuc
  
