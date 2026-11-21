HARIC = ("hizmeti alınacak", "danışmanlık", "ihale", "satılacak", "kiralanacak")


def kucult(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


def uygun(ilan):
    b = kucult(ilan["baslik"])
    return not any(k in b for k in HARIC)


def aciklama_yaz(ilan):
    s = ["📢 " + ilan["baslik"][:300]]
    ek = []
    if ilan["kurum"]:
        ek.append("🏛 " + ilan["kurum"])
    if ilan.get("bitis_yazi"):
        ek.append("⏰ Son başvuru: " + ilan["bitis_yazi"])
    if ek:
        s += [""] + ek
    s += [
        "",
        "📩 İş arayan birine gönder, sonra bakmak için kaydet 🔖",
        "",
        "Başvuru şartları ve ayrıntılar için resmî ilanı inceleyin:",
        "https://www.ilan.gov.tr/ilan/" + ilan["id"],
        "",
        "Kaynak: ilan.gov.tr",
        "ℹ️ Bağımsız bir derleme sayfasıdır, resmî kurum değildir.",
        "",
        "#kamuilan #kpss #kamupersonelalımı #memur #işilanı",
    ]
    return "\n".join(s)
# SON
