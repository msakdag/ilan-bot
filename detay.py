from playwright.sync_api import sync_playwright

from tarih import bugun, tarih_bul, tarih_yazi  # noqa: F401


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
# SON
