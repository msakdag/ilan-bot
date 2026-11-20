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
      
