from playwright.sync_api import sync_playwright

ISKUR = "https://www.iskur.gov.tr/ilanlar/kurumdisi-kamu-isci-alim-ilanlari/"
JS = """() => {
    const e = [...document.querySelectorAll('a,li,div,span,td')]
        .find(x => x.children.length === 0 && /^Adana/.test(x.innerText.trim()));
    return e ? e.parentElement.outerHTML.slice(0, 700) : 'Adana bulunamadi';
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    c = b.new_context(ignore_https_errors=True, locale="tr-TR")
    s = c.new_page()
    gorulen = []

    def yanit(r):
        tur = r.headers.get("content-type", "")
        if "json" in tur or "xml" in tur:
            try:
                ozet = r.text()[:150].replace("\n", " ")
            except Exception:
                ozet = "(okunamadi)"
            gorulen.append((r.status, r.request.method, r.url[:110], ozet))

    s.on("response", yanit)
    s.goto(ISKUR, wait_until="networkidle", timeout=60000)
    print("JSON/XML yanitlari:", len(gorulen))
    for g in gorulen[:12]:
        print(" -", g)
    print("--- Adana ogesinin cevresi ---")
    print(s.evaluate(JS))
    b.close()
# SON
