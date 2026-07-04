# -*- coding: utf-8 -*-
"""
generate_playlist.py

YouTube canlı yayınlarından yt-dlp ile taze HLS linklerini çeker ve
playlist.m3u dosyasını üretir. Git commit/push işlemini YAPMAZ -
onu GitHub Actions workflow'undaki ayrı adım hallediyor.

Bir kanal bu çalıştırmada başarısız olursa (geçici hata, rate limit vb.)
onceki_linkler.json'daki son başarılı linki kullanır, böylece playlist'ten
tamamen düşmez.
"""
import json
import subprocess

# Guncel ve dogrulanmis YouTube IPTV kanal listesi
kanallar = [
    ("trthaber", "TRT Haber", "https://www.youtube.com/@trthaber/live"),
    ("cnnturk", "CNN Turk", "https://www.youtube.com/@cnnturk/live"),
    ("ntv", "NTV", "https://www.youtube.com/@ntv/live"),
    ("ahaber", "A Haber", "https://www.youtube.com/@Ahaber/live"),
    ("haberturk", "Haber Turk", "https://www.youtube.com/@haberturktv/live"),
    ("halktv", "Halk TV", "https://www.youtube.com/@Halktvkanali/live"),
    ("sozcutelevizyonu", "Sozcu TV", "https://www.youtube.com/@sozcutelevizyonu/live"),
    ("tgrthaber", "TGRT Haber", "https://www.youtube.com/@tgrthaber/live"),
    ("flashhaber", "Flash Haber", "https://www.youtube.com/@flashhabertv/live"),
    ("haberglobal", "Haber Global", "https://www.youtube.com/@haberglobal/live"),
    ("tv100", "TV 100", "https://www.youtube.com/@tv100/live"),
    ("bloomberght", "Bloomberg HT", "https://www.youtube.com/@bloomberght/live"),
    ("benguturk", "Bengu Turk", "https://www.youtube.com/@tvbenguturk/live"),
    ("krttv", "KRT TV", "https://www.youtube.com/@krtcanli/live"),
    ("ulusalkanal", "Ulusal Kanal", "https://www.youtube.com/@ulusalkanaltv/live"),
    ("ulketv", "Ulke TV", "https://www.youtube.com/@ulketv/live"),
    ("ekoturk", "Eko Turk", "https://www.youtube.com/@ekoturktv/live"),
    ("tv24", "24 TV", "https://www.youtube.com/@YirmidortTV/live"),
    ("aspor", "A Spor", "https://www.youtube.com/@aspor/live"),
    ("htspor", "HT Spor", "https://www.youtube.com/@htspor/live"),
    ("tvnet", "TV Net", "https://www.youtube.com/@tvnet/live"),
    ("beinsportshaber", "Bein Spor Haber", "https://www.youtube.com/@beINSPORTSTurkiye/live"),
    ("cnbce", "CNBC-e", "https://www.youtube.com/@cnbce/live"),
]

ONCEKI_LINKLER_DOSYASI = "onceki_linkler.json"

try:
    with open(ONCEKI_LINKLER_DOSYASI, "r", encoding="utf-8") as f:
        onceki_linkler = json.load(f)
except FileNotFoundError:
    onceki_linkler = {}

yeni_linkler = dict(onceki_linkler)
ana_m3u = "#EXTM3U\n"
basarili_sayisi = 0

print("Kanal linkleri toplaniyor...\n")

for slug, isim, url in kanallar:
    link = None
    try:
        result = subprocess.run(
            ["yt-dlp", "--cookies", "cookies.txt", "-f", "best", "-g", url],
            capture_output=True, text=True, timeout=20
        )
        cikti = result.stdout.strip()
        if cikti and cikti.startswith("http"):
            link = cikti
            basarili_sayisi += 1
            print(f"OK: {isim} taze link alindi.")
        else:
            hata_ozeti = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "bos cikti"
            print(f"UYARI: {isim} - taze link alinamadi ({hata_ozeti[:150]})")
    except Exception as e:
        print(f"UYARI: {isim} - istisna olustu: {e}")

    if not link:
        if slug in onceki_linkler:
            link = onceki_linkler[slug]
            print("       -> onceki link ile devam ediliyor.")
        else:
            print(f"HATA: {isim} - onceki kayit da yok, atlaniyor.")
            continue

    yeni_linkler[slug] = link
    ana_m3u += f'#EXTINF:-1 tvg-name="{isim}" group-title="Canli" http-user-agent="VLC",{isim}\n{link}\n'

with open("playlist.m3u", "w", encoding="utf-8") as f:
    f.write(ana_m3u)

with open(ONCEKI_LINKLER_DOSYASI, "w", encoding="utf-8") as f:
    json.dump(yeni_linkler, f, ensure_ascii=False, indent=2)

print(f"\nToplam {len(yeni_linkler)} kanal playlist.m3u'da mevcut ({basarili_sayisi} taze).")
