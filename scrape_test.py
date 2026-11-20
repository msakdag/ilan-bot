import re

import requests
import urllib3

urllib3.disable_warnings()
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9",
}

URLS = [
    "https://www.ilan.gov.tr/sitemap/daily-ads.xml",
    "https://www.ilan.gov.tr/sitemap/ads.xml",
    "https://www.ilan.gov.tr/sitemap/categories.xml",
    "https://www.ilan.gov.tr/sitemap/daily-categories.xml",
    "https://kamuilan.sbb.gov.tr",
    "https://www.iskur.gov.tr/ilanlar/kamu-memur-alim-ilanlari",
    "https://www.iskur.gov.tr/ilanlar/kurumdisi-kamu-isci-alim-ilanlari/",
]

for url in URLS:
    try:
        r = requests.get(url, headers=HEADERS, timeout=30, verify=False)
        links = len(re.findall(r"<a\s", r.text))
        locs = len(re.findall(r"<loc>", r.text))
        print(r.status_code, "| boyut:", len(r.text), "| a:", links, "| loc:", locs, "|", url)
    except Exception as e:
        print("HATA |", url, "|", str(e)[:80])
        
