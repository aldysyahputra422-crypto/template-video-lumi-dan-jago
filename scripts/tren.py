"""Kumpulkan sinyal tren tanpa login: Google Trends Indonesia (RSS) dan Bilibili Populer (Tiongkok, API publik).

python -m scripts.tren   → JSON: judul + sinyal per sumber. Tidak memakai akun, kunci API, atau layanan berbayar.
Sumber yang tidak bisa dijangkau (Weibo 403, TikTok Creative Center butuh login) tidak dicoba; yang gagal dicatat, tidak menghentikan.
Tren mentah mayoritas olahraga dan berita: ini BAHAN untuk skill topik-reels (tema dan emosi yang sedang ramai), bukan daftar topik.
"""
import json
import re
import subprocess
import sys

GOOGLE = "https://trends.google.com/trending/rss?geo=ID"
BILIBILI = "https://api.bilibili.com/x/web-interface/popular?ps=30"


def _curl(url: str) -> str:
    return subprocess.run(["curl", "-sS", "-m", "20", "-A", "Mozilla/5.0", url], capture_output=True, text=True, check=True).stdout


def parse_google(xml: str) -> list[dict]:
    out = []
    for item in xml.split("<item>")[1:]:
        t = re.search(r"<title>(.*?)</title>", item, re.S)
        s = re.search(r"<ht:approx_traffic>(.*?)</ht:approx_traffic>", item, re.S)
        if t:
            out.append({"judul": t.group(1).strip(), "sinyal": s.group(1).strip() if s else ""})
    return out


def parse_bilibili(raw: str) -> list[dict]:
    d = json.loads(raw)
    return [{"judul": v["title"], "sinyal": f"{v['stat']['view']} tayangan", "kategori": v.get("tname", "")} for v in d.get("data", {}).get("list", [])]


def kumpulkan(ambil=_curl) -> dict:
    hasil = {"indonesia": {"google_trends": []}, "tiongkok": {"bilibili_populer": []}, "catatan": []}
    for kunci, grup, url, parse in (("google_trends", "indonesia", GOOGLE, parse_google), ("bilibili_populer", "tiongkok", BILIBILI, parse_bilibili)):
        try:
            hasil[grup][kunci] = parse(ambil(url))
        except Exception as e:  # noqa: BLE001
            hasil["catatan"].append(f"{kunci} gagal: {str(e)[:80]}")
    return hasil


if __name__ == "__main__":
    print(json.dumps(kumpulkan(), ensure_ascii=False, indent=1))
