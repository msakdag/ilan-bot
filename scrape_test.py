from playwright.sync_api import sync_playwright

ISKUR = "https://www.iskur.gov.tr/ilanlar/kurumdisi-kamu-isci-alim-ilanlari/"
SBB = "https://kamuilan.sbb.gov.tr"
JS = r"""els => els.filter(e => /\(\d+\)\s*$/.test(e.innerText.trim())
    && e.innerText.trim().length < 60 && e.children.length < 3)
    .slice(0, 8).map(e => [e.tagName, e.innerText.trim(),
    e.getAttribute('href') || '', e.getAttribute('onclick') || ''])"""

with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(ignore_https_errors=True, locale="tr-TR")

    print("===== SBB")
    s = c.new_page()
    try:
        r = s.goto(SBB, wait_until="networkidle", timeout=60000)
        print("Durum:", r.status if r else "?", "| baslik:", s.title())
        print(s.inner_text("body")[:300].replace("\n", " | "))
    except Exception as e:
        print("Hata:", str(e)[:100])
    s.close()

    print("===== ISKUR")
    s = c.new_page()
    s.goto(ISKUR, wait_until="networkidle", timeout=60000)
    ogeler = s.eval_on_selector_all("a, button, li, div", JS)
    for o in ogeler:
        print(" -", o)
    if ogeler:
        ad = ogeler[0][1]
        try:
            s.get_by_text(ad, exact=True).first.click()
            s.wait_for_timeout(3000)
            metin = s.inner_text("body")
            i = max(metin.find(ad), 0)
            print("Tiklandi:", ad)
            print(metin[i:i + 700].replace("\n", " | "))
        except Exception as e:
            print("Tiklama hatasi:", str(e)[:100])
    b.close()
# SON
