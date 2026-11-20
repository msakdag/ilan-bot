from PIL import ImageFont

from bot import FONT_KALIN


def ortala(d, metin, font, x, genislik, y, renk):
    w = d.textlength(metin, font=font)
    d.text((x + (genislik - w) / 2, y), metin, font=font, fill=renk)


def tarih_karti(d, ilan, W, kenar, ust):
    genislik = W - 2 * kenar
    d.rounded_rectangle([kenar, ust, W - kenar, ust + 170], radius=24,
                        fill="#173a6b", outline="#f2b705", width=4)
    d.text((kenar + 36, ust + 24), "SON BAŞVURU",
           font=ImageFont.truetype(FONT_KALIN, 30), fill="#f2b705")
    for boyut in (58, 52, 46, 40):
        df = ImageFont.truetype(FONT_KALIN, boyut)
        if d.textlength(ilan["bitis_yazi"], font=df) <= genislik - 296:
            break
    d.text((kenar + 36, ust + 78), ilan["bitis_yazi"], font=df, fill="#ffffff")
    px = W - kenar - 226
    d.rounded_rectangle([px, ust + 28, px + 190, ust + 142], radius=18, fill="#f2b705")
    kalan = ilan["kalan"]
    buyuk, kucuk = ("BUGÜN", "son gün") if kalan == 0 else (str(kalan), "gün kaldı")
    ortala(d, buyuk, ImageFont.truetype(FONT_KALIN, 50), px, 190, ust + 36, "#0f2747")
    ortala(d, kucuk, ImageFont.truetype(FONT_KALIN, 26), px, 190, ust + 100, "#0f2747")
