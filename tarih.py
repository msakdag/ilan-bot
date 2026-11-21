import re
from datetime import date, datetime, timedelta, timezone

AYLAR = ["", "ocak", "şubat", "mart", "nisan", "mayıs", "haziran",
         "temmuz", "ağustos", "eylül", "ekim", "kasım", "aralık"]
AYLAR_ADI = [a.capitalize() for a in AYLAR]
D = r"(\d{1,2})[\s./]+(\w+)[\s./]+(\d{4})"
DESENLER = [
    r"son\s+başvuru\s+(?:tarihi|günü)\s*[:\-]?\s*(?:olan\s+)?" + D,
    D + r"\s+bitiş\s+tarihinde",
]
ARALIK = re.compile(
    D + r"(?:\s*saat\s*\d{1,2}[:.]\d{2})?\s*(?:[-–—]|ile)\s*" + D, re.IGNORECASE)


def kucult(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


def bugun():
    return datetime.now(timezone(timedelta(hours=3))).date()


def tarih_yazi(t):
    return "%d %s %d" % (t.day, AYLAR_ADI[t.month], t.year)


def tarih_yap(gun, ay, yil):
    try:
        no = int(ay) if ay.isdigit() else AYLAR.index(kucult(ay))
        return date(int(yil), no, int(gun))
    except ValueError:
        return None


def tarih_bul(metin):
    for desen in DESENLER:
        for m in re.finditer(desen, metin, re.IGNORECASE):
            t = tarih_yap(*m.groups())
            if t:
                return t
    for m in ARALIK.finditer(metin):
        cevre = metin[max(0, m.start() - 150): m.end() + 100]
        if "başvuru" in kucult(cevre):
            t = tarih_yap(*m.groups()[3:])
            if t:
                return t
    return None
# SON
