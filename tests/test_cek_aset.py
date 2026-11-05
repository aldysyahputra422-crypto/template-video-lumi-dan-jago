"""Pemeriksa aset per video: isi bebas, gaya terkunci (palet terukur, tanpa sumber luar), semua aset terdeklarasi ada."""
import shutil
from pathlib import Path

from scripts import cek_aset, naskah_format as nf

ROOT = Path(__file__).resolve().parents[1]
F = ROOT / "tests/fixtures/aset_uji"


def _folder(tmp_path, aset_js=None):
    f = tmp_path / "v"
    f.mkdir()
    n = nf.urai((F / "tempelan.txt").read_text(encoding="utf-8")).naskah
    (f / "naskah.json").write_text(__import__("json").dumps(n), encoding="utf-8")
    if aset_js is not None:
        (f / "aset.js").write_text(aset_js, encoding="utf-8")
    return f


def test_aset_lengkap_dan_sesuai_gaya_lolos_dengan_lembar(tmp_path):
    f = _folder(tmp_path, (F / "aset.js").read_text(encoding="utf-8"))
    h = cek_aset.periksa(f, lembar=True)
    assert h["galat"] == [], h["galat"]
    assert (f / "aset-cek.png").exists()


def test_aset_hilang_dan_pelanggaran_gaya_ditolak(tmp_path):
    js = (F / "aset.js").read_text(encoding="utf-8").replace("keju: () =>", "roti: () =>")
    js = js.replace("fill=\"${C.cahaya}\"", "fill=\"#00FF66\"").replace("return {", "const x = '<image href=\"http://a.b/c.png\"/>';\n  return {")
    h = cek_aset.periksa(_folder(tmp_path, js), lembar=False)
    pesan = " ".join(h["galat"])
    assert "keju" in pesan and "#00FF66" in pesan and "luar" in pesan


def test_aksen_khusus_maksimal_tiga(tmp_path):
    js = (F / "aset.js").read_text(encoding="utf-8").replace("aksen: []", "aksen: ['#00FF66']").replace("fill=\"${C.cahaya}\"", "fill=\"#00FF66\"")
    assert cek_aset.periksa(_folder(tmp_path, js), lembar=False)["galat"] == []
    js2 = js.replace("aksen: ['#00FF66']", "aksen: ['#00FF66', '#FF0000', '#0000FF', '#FF00FF']")
    assert any("aksen" in g for g in cek_aset.periksa(_folder(tmp_path / "b" if (tmp_path / "b").mkdir() is None else tmp_path, js2), lembar=False)["galat"])


def test_tanpa_aset_js_daftar_kebutuhan(tmp_path):
    h = cek_aset.periksa(_folder(tmp_path), lembar=False)
    assert any("aset.js belum ada" in g for g in h["galat"])
    teks = (tmp_path / "v/aset-dibutuhkan.md").read_text(encoding="utf-8")
    assert "sumur_tua" in teks and "tikus" in teks and "ketukan 1" in teks
