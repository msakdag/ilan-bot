from PIL import Image, ImageDraw, ImageFont

from bot import FONT_KALIN, FONT_NORMAL, sar
from kart import tarih_karti


def gorsel_uret(ilan, yol):
    W, kenar = 1080, 80
    genislik = W - 2 * kenar
    img = Image.new("RGB", (W, W), "#0f2747")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 18], fill="#f2b705")

    ef = ImageFont.truetype(FONT_KALIN, 38)
    etiket = "KAMU PERSONEL ALIMI"
    ew = d.textlength(etiket, font=ef)
    d.rounded_rectangle([kenar, 80, kenar + ew + 56, 160], radius=16, fill="#f2b705")
    d.text((kenar + 28, 99), etiket, font=ef, fill="#0f2747")

    y = 205
    if ilan["kurum"]:
        kf = ImageFont.truetype(FONT_KALIN, 36)
        for s in sar(d, ilan["kurum"], kf, genislik)[:3]:
            d.text((kenar, y), s, font=kf, fill="#9fc3ff")
            y += 50
        y += 24

    tarihli = bool(ilan.get("bitis"))
    alt = 700 if tarihli else 860
    for boyut in (64, 56, 48, 42, 36):
        f = ImageFont.truetype(FONT_KALIN, boyut)
        satirlar = sar(d, ilan["baslik"][:220], f, genislik)
        yuk = int(boyut * 1.32)
        if len(satirlar) * yuk <= alt - y:
            break
    for s in satirlar:
        d.text((kenar, y), s, font=f, fill="#ffffff")
        y += yuk

    if tarihli:
        tarih_karti(d, ilan, W, kenar, 730)

    d.rectangle([kenar, 940, W - kenar, 943], fill="#2c4a75")
    d.text((kenar, 975), "Kaynak: ilan.gov.tr  |  İlan No: " + ilan["id"],
           font=ImageFont.truetype(FONT_NORMAL, 32), fill="#c9d6ea")
    img.save(yol, "JPEG", quality=92)
  
