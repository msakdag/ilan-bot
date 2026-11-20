import json
import os
import re
import sys
import time

import requests
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

LISTE_URL = "https://www.ilan.gov.tr/ilan/kategori/44/kamu-personel-alim-ve-sinavlari"
KATEGORI = "kamu-personel-alim-ve-sinavlari"
DURUM_DOSYASI = "durum/paylasilan.json"
BEKLEYEN_DOSYASI = "bekleyen.json"
API = "https://graph.facebook.com/v27.0"

FONT_KALIN = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_NORMAL = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


# ---------- Kayit (daha once paylasilanlar) ----------
def durum_oku():
    try:
        with open(DURUM_DOSYASI, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def durum_yaz(idler):
    os.makedirs("durum", exist_ok=True)
    with open(DURUM_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(idler, f, ensure_ascii=False, indent=1)


# ---------- Ilanlari cekme ----------
def metni_ayir(metin):
    """Baglanti metninden kurum (BUYUK HARF) ve baslik kismini ayirir."""
    satirlar = [s.strip() for s in metin.split("\n") if s.strip()]
    kurum, baslik = "", ""
    for s in satirlar:
        if not kurum and s == s.upper() and len(s) > 5:
            kurum = s
        elif not baslik:
            baslik = s
    if not baslik:
        baslik = kurum
        kurum = ""
    baslik = re.sub(r"\b[A-Z]{3}\d{5,}\b", "", baslik)
    baslik = re.sub(r"\s+", " ", baslik).strip(" -")
    return kurum, baslik


def ilanlari_cek():
    with sync_playwright() as p:
        tarayici = p.chromium.launch()
        baglam = tarayici.new_context(ignore_https_errors=True, locale="tr-TR")
        sayfa = baglam.new_page()
        sayfa.goto(LISTE_URL, wait_until="networkidle", timeout=60000)
        baglantilar = sayfa.eval_on_selector_all(
            "a[href]", "els => els.map(e => [e.innerText.trim(), e.href])"
        )
        tarayici.close()
      
    ilanlar = {}
    for metin, href in baglantilar:
        m = re.search(r"/ilan/(\d+)/", href)
        if not m or KATEGORI not in href:
            continue
        ilan_id = m.group(1)
        if ilan_id in ilanlar and len(metin) <= len(ilanlar[ilan_id]["ham"]):
            continue
        ilanlar[ilan_id] = {"id": ilan_id, "url": href, "ham": metin}

    sonuc = []
    for i in ilanlar.values():
        i["kurum"], i["baslik"] = metni_ayir(i["ham"])
        sonuc.append(i)
    return sonuc


# ---------- Gorsel uretme ----------
def sar(cizim, metin, font, genislik):
    satirlar, satir = [], ""
    for kelime in metin.split():
        deneme = (satir + " " + kelime).strip()
        if cizim.textlength(deneme, font=font) <= genislik:
            satir = deneme
        else:
            if satir:
                satirlar.append(satir)
            satir = kelime
    if satir:
        satirlar.append(satir)
    return satirlar
    
def gorsel_uret(ilan, yol):
    W = H = 1080
    kenar = 80
    icerik_genislik = W - 2 * kenar
    img = Image.new("RGB", (W, H), "#0f2747")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 18], fill="#f2b705")

    etiket_font = ImageFont.truetype(FONT_KALIN, 38)
    etiket = "KAMU PERSONEL ALIMI"
    etiket_w = d.textlength(etiket, font=etiket_font)
    d.rounded_rectangle([kenar, 80, kenar + etiket_w + 56, 160], radius=16, fill="#f2b705")
    d.text((kenar + 28, 99), etiket, font=etiket_font, fill="#0f2747")

    y = 210
    if ilan["kurum"]:
        kurum_font = ImageFont.truetype(FONT_KALIN, 38)
        for s in sar(d, ilan["kurum"], kurum_font, icerik_genislik)[:3]:
            d.text((kenar, y), s, font=kurum_font, fill="#9fc3ff")
            y += 52
        y += 30

    mevcut = 860 - y
    baslik = ilan["baslik"][:220]
    for boyut in (66, 58, 50, 44, 38):
        font = ImageFont.truetype(FONT_KALIN, boyut)
        satirlar = sar(d, baslik, font, icerik_genislik)
        satir_yuksekligi = int(boyut * 1.35)
        if len(satirlar) * satir_yuksekligi <= mevcut:
            break
    for s in satirlar:
        d.text((kenar, y), s, font=font, fill="#ffffff")
        y += satir_yuksekligi

    d.rectangle([kenar, 940, W - kenar, 943], fill="#2c4a75")
    alt_font = ImageFont.truetype(FONT_NORMAL, 32)
    d.text((kenar, 975), "Kaynak: ilan.gov.tr  |  İlan No: " + ilan["id"], font=alt_font, fill="#c9d6ea")
    img.save(yol, "JPEG", quality=92)


def aciklama_yaz(ilan):
    satirlar = ["📢 " + ilan["baslik"][:300], ""]
    if ilan["kurum"]:
        satirlar.append("🏛 " + ilan["kurum"])
        satirlar.append("")
    satirlar += [
        "Başvuru şartları ve ayrıntılar için resmî ilanı inceleyin:",
        ilan["url"],
        "",
        "Kaynak: ilan.gov.tr",
        "",
        "#kamuilan #kpss #kamupersonelalımı #memur #işilanı",
    ]
    return "\n".join(satirlar)
    
# ---------- Adim 1: cek ve gorsel uret ----------
def uret():
    adet = int(os.environ.get("ADET") or 1)
    gorulmus = set(durum_oku())
    ilanlar = ilanlari_cek()
    print("Listede bulunan ilan:", len(ilanlar))
    for i in ilanlar[:2]:
        print("Ham metin ornegi:", repr(i["ham"]))
    yeniler = [i for i in ilanlar if i["id"] not in gorulmus]
    print("Daha once paylasilmamis:", len(yeniler))

    secilen = yeniler[:adet]
    os.makedirs("gorseller", exist_ok=True)
    for i in secilen:
        gorsel_uret(i, "gorseller/" + i["id"] + ".jpg")
        print("Gorsel uretildi:", i["id"], "|", i["kurum"], "|", i["baslik"][:80])
    with open(BEKLEYEN_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(secilen, f, ensure_ascii=False)


# ---------- Adim 2: Instagram'a paylas ----------
def istek(yontem, adres, **kwargs):
    r = requests.request(yontem, adres, timeout=60, **kwargs)
    if not r.ok:
        raise RuntimeError(str(r.status_code) + " " + r.text[:300])
    return r.json()
    
def paylas():
    user_id = os.environ["IG_USER_ID"]
    token = os.environ["IG_ACCESS_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]

    with open(BEKLEYEN_DOSYASI, encoding="utf-8") as f:
        bekleyen = json.load(f)
    if not bekleyen:
        print("Paylasilacak yeni ilan yok.")
        return

    gorulmus = durum_oku()
    basarili, hatali = 0, 0
    for ilan in bekleyen:
        gorsel_url = "https://raw.githubusercontent.com/" + repo + "/main/gorseller/" + ilan["id"] + ".jpg"
        try:
            kap = istek("POST", API + "/" + user_id + "/media", data={
                "image_url": gorsel_url,
                "caption": aciklama_yaz(ilan),
                "access_token": token,
            })
            kap_id = kap["id"]
            for _ in range(12):
                durum = istek("GET", API + "/" + kap_id, params={
                    "fields": "status_code", "access_token": token})
                if durum.get("status_code") == "FINISHED":
                    break
                if durum.get("status_code") == "ERROR":
                    raise RuntimeError("Gorsel islenemedi: " + str(durum))
                time.sleep(5)
            sonuc = istek("POST", API + "/" + user_id + "/media_publish", data={
                "creation_id": kap_id, "access_token": token})
            print("PAYLASILDI:", ilan["id"], "| gonderi:", sonuc.get("id"))
            gorulmus.append(ilan["id"])
            durum_yaz(gorulmus)
            basarili += 1
            time.sleep(5)
        except Exception as e:
            print("HATA:", ilan["id"], "|", str(e)[:300])
            hatali += 1
    if hatali and not basarili:
        sys.exit(1)


if __name__ == "__main__":
    komut = sys.argv[1] if len(sys.argv) > 1 else ""
    if komut == "uret":
        uret()
    elif komut == "paylas":
        paylas()
    else:
        print("Kullanim: python bot.py uret | paylas")
        
