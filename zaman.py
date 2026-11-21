import json
import os
import sys
from datetime import datetime, timedelta, timezone

DOSYA = "durum/saatler.json"
PENCERELER = {"ogle": (11.5, 16.0), "aksam": (19.5, 23.0)}


def simdi():
    return datetime.now(timezone(timedelta(hours=3)))


def pencere(t):
    saat = t.hour + t.minute / 60
    for ad, (bas, bit) in PENCERELER.items():
        if bas <= saat < bit:
            return t.strftime("%Y-%m-%d") + "-" + ad
    return None


def oku():
    try:
        with open(DOSYA, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def karar():
    t = simdi()
    anahtar = pencere(t)
    if os.environ.get("OLAY") != "schedule":
        calis, neden = True, "elle calistirma"
    elif anahtar is None:
        calis, neden = False, "paylasim penceresi disinda"
    elif anahtar in oku():
        calis, neden = False, "bu pencerede zaten paylasildi"
    else:
        calis, neden = True, "pencere acik: " + anahtar
    print(t.strftime("%H:%M"), "TSI |", neden)
    cikti = os.environ.get("GITHUB_OUTPUT")
    if cikti:
        with open(cikti, "a") as f:
            f.write("calis=" + str(calis).lower() + "\n")


def kaydet():
    anahtar = pencere(simdi())
    if not anahtar:
        return
    veri = oku()
    veri[anahtar] = simdi().isoformat(timespec="minutes")
    veri = {k: veri[k] for k in sorted(veri)[-30:]}
    os.makedirs("durum", exist_ok=True)
    with open(DOSYA, "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=1)
    print("Pencere kaydedildi:", anahtar)


if __name__ == "__main__":
    komut = sys.argv[1] if len(sys.argv) > 1 else ""
    if komut == "karar":
