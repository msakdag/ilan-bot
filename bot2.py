import json
import os
import sys

import bot
import detay
import gorsel2


def aciklama_yaz(ilan):
    s = ["📢 " + ilan["baslik"][:300], ""]
    if ilan["kurum"]:
        s += ["🏛 " + ilan["kurum"], ""]
    if ilan.get("bitis_yazi"):
        s += ["⏰ Son başvuru: " + ilan["bitis_yazi"], ""]
    s += ["Başvuru şartları ve ayrıntılar için resmî ilanı inceleyin:", ilan["url"], "",
          "Kaynak: ilan.gov.tr", "",
          "#kamuilan #kpss #kamupersonelalımı #memur #işilanı"]
    return "\n".join(s)


def uret():
    adet = int(os.environ.get("ADET") or 1)
    gorulmus = set(bot.durum_oku())
    yeniler = [i for i in bot.ilanlari_cek() if i["id"] not in gorulmus]
    print("Daha once paylasilmamis:", len(yeniler))
    aday = yeniler[: adet + 5]
    metinler = detay.detay_getir([i["url"] for i in aday])
    bugun = detay.bugun()
    secilen = []
    for i in aday:
        if len(secilen) >= adet:
            break
        t = detay.tarih_bul(metinler.get(i["url"], ""))
        if t and t < bugun:
            print("Suresi gecmis, atlandi:", i["id"], t)
            continue
        if t:
            i["bitis"], i["bitis_yazi"] = t.isoformat(), detay.tarih_yazi(t)
            i["kalan"] = (t - bugun).days
        else:
            print("Tarih bulunamadi:", i["id"])
        secilen.append(i)
    os.makedirs("gorseller", exist_ok=True)
    for i in secilen:
        gorsel2.gorsel_uret(i, "gorseller/" + i["id"] + ".jpg")
        print("Gorsel:", i["id"], i["baslik"][:50], "| bitis:", i.get("bitis"))
    with open(bot.BEKLEYEN_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(secilen, f, ensure_ascii=False)


if __name__ == "__main__":
    bot.aciklama_yaz = aciklama_yaz
    komut = sys.argv[1] if len(sys.argv) > 1 else ""
    if komut == "uret":
        uret()
    elif komut == "paylas":
        bot.paylas()
    else:
        print("Kullanim: python bot2.py uret | paylas")
      
