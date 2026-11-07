import json

from scripts import tren

RSS = """<rss xmlns:ht="x"><channel><item><title>minyak sawit</title><ht:approx_traffic>100+</ht:approx_traffic></item>
<item><title>hujan meteor</title><ht:approx_traffic>200+</ht:approx_traffic></item></channel></rss>"""
BILI = json.dumps({"code": 0, "data": {"list": [{"title": "假如短剧是违禁品", "stat": {"view": 490946}, "tname": "搞笑"}]}})


def test_parse_google_trends_dan_bilibili():
    g = tren.parse_google(RSS)
    assert g == [{"judul": "minyak sawit", "sinyal": "100+"}, {"judul": "hujan meteor", "sinyal": "200+"}]
    b = tren.parse_bilibili(BILI)
    assert b == [{"judul": "假如短剧是违禁品", "sinyal": "490946 tayangan", "kategori": "搞笑"}]


def test_kumpulkan_tahan_bila_satu_sumber_gagal():
    def ambil(url):
        if "bilibili" in url:
            raise OSError("diblokir")
        return RSS
    h = tren.kumpulkan(ambil=ambil)
    assert h["indonesia"]["google_trends"][0]["judul"] == "minyak sawit"
    assert h["tiongkok"]["bilibili_populer"] == [] and "diblokir" in h["catatan"][0]
