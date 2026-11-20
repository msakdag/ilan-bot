import requests
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9",
}

PAGES = [
    "https://www.iskur.gov.tr/ilanlar/kamu-memur-alim-ilanlari",
    "https://www.iskur.gov.tr/ilanlar/kurumdisi-kamu-isci-alim-ilanlari/",
]

for url in PAGES:
    r = requests.get(url, headers=HEADERS, timeout=30, verify=False)
    soup = BeautifulSoup(r.text, "html.parser")
    print("=====", url, "|", r.status_code)
    print("tablo:", len(soup.find_all("table")),
          "| tr:", len(soup.find_all("tr")),
          "| li:", len(soup.find_all("li")))

    bulunan = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        metin = a.get_text(" ", strip=True)
        pdf = ".pdf" in href.lower()
        ilan_gibi = "ilan" in href.lower() and len(metin) > 25
        if pdf or ilan_gibi:
            bulunan.append((metin[:90], href[:120]))

    print("ilan benzeri baglanti:", len(bulunan))
    for metin, href in bulunan[:12]:
        print(" -", metin, "|", href)
        
