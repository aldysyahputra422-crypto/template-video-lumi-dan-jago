"""Tempelan ChatGPT (format blok) → naskah.json, MEKANIS: tanpa LLM, galat per baris.

python -m scripts.naskah_format <folder> [tempelan.txt] [--timpa]
Kode: 0 jadi, 1 ada galat (lihat <folder>/koreksi-chatgpt.md), 7 menolak menimpa naskah yang sudah disetujui.
Format lengkap dan contoh: scripts/prompt_naskah.py dan contoh/tenggat-planning-fallacy/tempelan.txt.
"""
import functools
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from scripts import tag as tag_mod

ROOT = Path(__file__).resolve().parents[1]
SKEMA = json.loads((ROOT / "schemas/naskah.schema.json").read_text(encoding="utf-8"))
LABEL = ("UCAP", "LATAR", "AKTOR", "AKSI", "EKSPRESI", "PROPS", "TEKS", "DATA", "KARTU", "ATA", "KAMERA", "KELUAR", "FAKTA", "SISIPAN", "SUASANA")
TEMPAT = ("jauh_kiri", "kiri", "tengah", "kanan", "jauh_kanan", "atas")


@functools.lru_cache(maxsize=None)
def kosakata() -> dict:
    return yaml.safe_load((ROOT / "config/kosakata.yaml").read_text(encoding="utf-8"))


@functools.lru_cache(maxsize=None)
def pose_ata() -> list[str]:
    return yaml.safe_load((ROOT / "config/tokoh.yaml").read_text(encoding="utf-8"))["tokoh"]["ata"]["pose"]


@dataclass
class Galat:
    baris: int | None
    pesan: str
    isi: str = ""

    def __str__(self) -> str:
        return f"baris {self.baris}: {self.pesan}" if self.baris else f"umum: {self.pesan}"


@dataclass
class Hasil:
    naskah: dict | None
    galat: list[Galat] = field(default_factory=list)


def token(teks: str) -> list[str]:
    return re.findall(r"[0-9]+(?:[.,][0-9]+)?|[\w-]+", teks.lower())


def _bersih(s: str) -> str:
    s = re.sub(r"^(?:[>\-*•]\s+)+", "", s.strip())
    return s.replace("**", "").replace("__", "").replace("`", "").strip()


class _Urai:
    def __init__(self, teks: str):
        self.mentah = teks.splitlines()
        self.galat: list[Galat] = []
        self.k = kosakata()
        self.meta = {"id": None, "judul": None, "sumber": None}
        self.ketukan: list[dict] = []

    def err(self, no, pesan):
        self.galat.append(Galat(no, pesan, self.mentah[no - 1].strip() if no else ""))

    def isyarat(self, no, s: str, kt: dict) -> tuple[str, str | None]:
        """Pisahkan '@kata' di akhir isian; pastikan kata itu ada di UCAP ketukan."""
        m = re.search(r"\s@([^\s@]+)\s*$", " " + s)
        if not m:
            return s.strip(), None
        kata = m.group(1).lower().strip(".,!?")
        isi = re.sub(r"\s*@[^\s@]+\s*$", "", s).strip()
        tk = token(kt.get("ucap", ""))
        if kata not in tk and not (len(kata) >= 4 and any(t.startswith(kata) for t in tk)):
            self.err(no, f"@{kata} tidak ada di UCAP ketukan ini: \"{kt.get('ucap', '')}\"")
        return isi, kata

    def baca(self):
        kt = None
        pemeran: set[str] = set()
        latar = None
        suasana = "normal"
        selesai = False
        for no, mentah in enumerate(self.mentah, 1):
            s = _bersih(mentah)
            if not s or s.startswith("```") or selesai:
                continue
            if re.match(r"^#{1,3}\s*AKHIR\b", s, re.I):
                selesai = True
                continue
            m = re.match(r"^#{1,3}\s*VIDEO\s+(\S+)\s*[|:]\s*(.+)$", s, re.I)
            if m:
                self.meta["id"], self.meta["judul"] = m.group(1), m.group(2).strip()
                continue
            m = re.match(r"^#{1,3}\s*SUMBER\s+(\S+)", s, re.I)
            if m:
                self.meta["sumber"] = m.group(1)
                continue
            m = re.match(r"^#{1,3}\s*KETUKAN\s*(\d+)", s, re.I)
            if m:
                kt = {"no": len(self.ketukan) + 1, "baris": no, "ucap": "", "ucap_el": "", "tag": [], "latar": latar, "aktor": [], "aksi": [],
                      "ekspresi": [], "props": [], "teks": [], "data": [], "kartu": None, "ata": None, "kamera": None, "keluar": [], "fakta": False, "sisipan": None, "suasana": suasana}
                self.ketukan.append(kt)
                continue
            if kt is None:
                continue  # obrolan ChatGPT sebelum blok pertama
            m = re.match(r"^([A-Za-z_]+)\s*:\s*(.*)$", s)
            if not m or m.group(1).upper() not in LABEL:
                self.err(no, f"baris tidak dikenal: '{s[:50]}'. Label: {', '.join(LABEL)}")
                continue
            lab, isi = m.group(1).upper(), m.group(2).strip()
            if "—" in isi:
                self.err(no, "berisi tanda pisah panjang (—); ganti koma atau titik")
            if lab == "UCAP":
                try:
                    kt["ucap"], kt["tag"], kt["ucap_el"] = tag_mod.pisah(isi)
                except tag_mod.TagTidakDikenal as e:
                    self.err(no, str(e))
                    kt["ucap"] = re.sub(r"\[[^\]]*\]", "", isi).strip()
                if not kt["ucap"]:
                    self.err(no, "UCAP kosong")
            elif lab == "LATAR":
                if isi not in self.k["latar"]:
                    self.err(no, f"latar tidak dikenal: {isi}. Latar: {', '.join(self.k['latar'])}")
                latar = kt["latar"] = isi
                pemeran = set()
            elif lab == "AKTOR":
                for a in [x.strip() for x in isi.split(";") if x.strip()]:
                    mm = re.match(r"^(\w+)\s*=\s*(\w+)(?:\s+(\w+))?(?:\s+(\w+))?$", a)
                    if not mm:
                        self.err(no, f"AKTOR harus: id=peran [posisi] [ekspresi], bukan '{a}'")
                        continue
                    i, peran, pos, eks = mm.group(1), mm.group(2), mm.group(3) or "tengah", mm.group(4) or "datar"
                    if peran not in self.k["peran"]:
                        self.err(no, f"peran tidak dikenal: {peran}. Peran: {', '.join(self.k['peran'])}")
                    if pos not in self.k["posisi"]:
                        self.err(no, f"posisi tidak dikenal: {pos}. Posisi: {', '.join(self.k['posisi'])}")
                    if eks not in self.k["ekspresi"]:
                        self.err(no, f"ekspresi tidak dikenal: {eks}. Ekspresi: {', '.join(self.k['ekspresi'])}")
                    pemeran.add(i)
                    kt["aktor"].append({"id": i, "peran": peran, "posisi": pos, "ekspresi": eks})
            elif lab == "AKSI":
                for a in [x.strip() for x in isi.split(";") if x.strip()]:
                    a, kata = self.isyarat(no, a, kt)
                    b = a.split()
                    if len(b) < 2:
                        self.err(no, f"AKSI harus: id aksi [ke posisi] [@kata], bukan '{a}'")
                        continue
                    if b[0] not in pemeran:
                        self.err(no, f"aktor belum ada: {b[0]} (tambahkan di AKTOR sesudah LATAR terakhir)")
                    if b[1] not in self.k["aksi"]:
                        self.err(no, f"aksi tidak dikenal: {b[1]}. Aksi: {', '.join(self.k['aksi'])}")
                    ke = b[3] if len(b) >= 4 and b[2] == "ke" else None
                    if ke and ke not in self.k["posisi"]:
                        self.err(no, f"posisi tidak dikenal: {ke}")
                    kt["aksi"].append({"id": b[0], "aksi": b[1], "ke": ke, "kata": kata})
            elif lab == "EKSPRESI":
                for a in [x.strip() for x in isi.split(";") if x.strip()]:
                    a, kata = self.isyarat(no, a, kt)
                    b = a.split()
                    if len(b) != 2:
                        self.err(no, f"EKSPRESI harus: id ekspresi [@kata], bukan '{a}'")
                        continue
                    if b[0] not in pemeran:
                        self.err(no, f"aktor belum ada: {b[0]}")
                    if b[1] not in self.k["ekspresi"]:
                        self.err(no, f"ekspresi tidak dikenal: {b[1]}. Ekspresi: {', '.join(self.k['ekspresi'])}")
                    kt["ekspresi"].append({"id": b[0], "ekspresi": b[1], "kata": kata})
            elif lab == "PROPS":
                for a in [x.strip() for x in isi.split(";") if x.strip()]:
                    a, kata = self.isyarat(no, a, kt)
                    b = a.split()
                    if len(b) < 2:
                        self.err(no, f"PROPS harus: nama tempat [gerak] [@kata], bukan '{a}'")
                        continue
                    if b[0] not in self.k["props"]:
                        self.err(no, f"props tidak dikenal: {b[0]}. Props: {', '.join(self.k['props'])}")
                    tp = b[1]
                    if ":" in tp:
                        jenis, sid = tp.split(":", 1)
                        if jenis not in ("tangan", "kepala") or sid not in pemeran:
                            self.err(no, f"tempat props tidak valid: {tp} (pakai tangan:<id> atau kepala:<id> aktor yang ada)")
                    elif tp not in TEMPAT:
                        self.err(no, f"tempat props tidak dikenal: {tp}. Tempat: {', '.join(TEMPAT)}, tangan:<id>, kepala:<id>")
                    gerak = b[2] if len(b) > 2 else "muncul"
                    if gerak not in self.k["gerak_props"]:
                        self.err(no, f"gerak props tidak dikenal: {gerak}. Gerak: {', '.join(self.k['gerak_props'])}")
                    kt["props"].append({"nama": b[0], "tempat": tp, "gerak": gerak, "kata": kata})
            elif lab == "TEKS":
                t, kata = self.isyarat(no, isi, kt)
                if len(t) > 32:
                    self.err(no, f"TEKS terlalu panjang ({len(t)} huruf, maksimal 32)")
                kt["teks"].append({"teks": t, "kata": kata})
            elif lab == "DATA":
                for a in [x.strip() for x in isi.split(";") if x.strip()]:
                    a, kata = self.isyarat(no, a, kt)
                    mm = re.match(r"^(.+?)\s*=\s*([0-9]+(?:[.,][0-9]+)?)\s*(.*)$", a)
                    if not mm:
                        self.err(no, f"DATA harus: label=angka [satuan] [@kata], bukan '{a}'")
                        continue
                    kt["data"].append({"label": mm.group(1).strip().replace("_", " "), "nilai": float(mm.group(2).replace(",", ".")), "satuan": mm.group(3).strip(), "kata": kata})
                    kt["fakta"] = True
            elif lab == "KARTU":
                bag = [x.strip() for x in isi.split("|")]
                if len(bag) < 2:
                    self.err(no, "KARTU harus: judul | butir 1 | butir 2 | butir 3")
                    continue
                butir = []
                for b in bag[1:]:
                    mm = re.match(r"^(.*?)\s*@([^\s@]+)\s*$", b)
                    butir.append({"teks": mm.group(1).strip(), "kata": mm.group(2).lower()} if mm else {"teks": b, "kata": None})
                if len(butir) > 3:
                    self.err(no, f"KARTU maksimal 3 butir (ada {len(butir)})")
                kt["kartu"] = {"judul": bag[0], "butir": butir}
            elif lab == "ATA":
                b = isi.split()
                if not b or b[0] not in pose_ata():
                    self.err(no, f"pose ata tidak dikenal: {b[0] if b else ''}. Pose: {', '.join(pose_ata())}")
                    continue
                tempat = b[1] if len(b) > 1 else "kanan"
                masuk = b[2] if len(b) > 2 else "pop"
                if tempat not in self.k["ata_tempat"] or masuk not in self.k["ata_masuk"]:
                    self.err(no, f"ATA harus: pose [{'|'.join(self.k['ata_tempat'])}] [{'|'.join(self.k['ata_masuk'])}]")
                kt["ata"] = {"pose": b[0], "tempat": tempat, "masuk": masuk}
            elif lab == "KAMERA":
                b = isi.split()
                if not b or b[0] not in self.k["kamera"]:
                    self.err(no, f"kamera tidak dikenal: {isi}. Kamera: {', '.join(self.k['kamera'])}")
                    continue
                if b[0] == "dekat" and (len(b) < 2 or b[1] not in pemeran):
                    self.err(no, "KAMERA dekat harus menyebut id aktor yang ada")
                kt["kamera"] = {"jenis": b[0], "target": b[1] if len(b) > 1 else None}
            elif lab == "SUASANA":
                if isi not in self.k["suasana"]:
                    self.err(no, f"suasana tidak dikenal: {isi}. Suasana: {', '.join(self.k['suasana'])}")
                    continue
                suasana = kt["suasana"] = isi
            elif lab == "SISIPAN":
                s_isi, kata = self.isyarat(no, isi, kt)
                b = s_isi.split()
                S = self.k["sisipan"]
                if not b or b[0] not in S:
                    self.err(no, f"sisipan tidak dikenal: {b[0] if b else ''}. Sisipan: {', '.join(S)}")
                    continue
                pilihan = list(self.k["props"]) if S[b[0]]["isi"] == "props" else S[b[0]]["isi"]
                isi_s = b[1] if len(b) > 1 else (pilihan[0] if pilihan else None)
                if len(b) > 1 and isi_s not in pilihan:
                    self.err(no, f"isi sisipan {b[0]} tidak dikenal: {isi_s}. Isi: {', '.join(pilihan) or '(tanpa isi)'}")
                if kt["sisipan"]:
                    self.err(no, "satu ketukan maksimal satu SISIPAN")
                kt["sisipan"] = {"nama": b[0], "isi": isi_s, "kata": kata}
            elif lab == "KELUAR":
                for i in [x.strip() for x in isi.split(";") if x.strip()]:
                    pemeran.discard(i)
                    kt["keluar"].append(i)
            elif lab == "FAKTA":
                kt["fakta"] = kt["fakta"] or isi.lower() in ("ya", "y", "true")
        if not self.meta["id"]:
            self.err(None, "tidak ada baris ##VIDEO <id> | <judul>")
        if len(self.ketukan) < 3:
            self.err(None, "minimal 3 ##KETUKAN")
        for kt in self.ketukan:
            if not kt["ucap"]:
                self.err(kt["baris"], f"ketukan {kt['no']} tanpa UCAP")
            if not kt["latar"]:
                self.err(kt["baris"], f"ketukan {kt['no']} belum punya LATAR (ketukan pertama wajib LATAR)")


def urai(teks: str) -> Hasil:
    u = _Urai(teks)
    u.baca()
    u.galat.sort(key=lambda g: (g.baris is None, g.baris or 0))
    if u.galat:
        return Hasil(None, u.galat)
    return Hasil({"id": u.meta["id"], "judul": u.meta["judul"], "sumber": u.meta["sumber"], "disetujui": False, "ketukan": u.ketukan})


def pesan_koreksi(galat: list) -> str:
    b = ["Naskahmu belum lulus pemeriksaan otomatis. Perbaiki HANYA baris di bawah, jangan ubah yang lain,",
         "pertahankan format blok (##VIDEO, ##KETUKAN, UCAP:, LATAR: dst), lalu kirim ulang SELURUH naskah.", ""]
    b += [f"- {g}" + (f"  → isi baris: `{g.isi[:140]}`" if getattr(g, "isi", "") else "") for g in galat]
    return "\n".join(b) + "\n"


def proses(folder: Path, sumber: Path | None = None, timpa: bool = False) -> tuple[int, list[str], Hasil | None]:
    folder = Path(folder)
    try:
        teks = (sumber or folder / "tempelan.txt").read_text(encoding="utf-8")
    except OSError as e:
        return 1, [f"tempelan tidak terbaca: {e}"], None
    tujuan = folder / "naskah.json"
    if tujuan.exists() and not timpa:
        try:
            if json.loads(tujuan.read_text(encoding="utf-8")).get("disetujui"):
                return 7, ["naskah.json sudah disetujui; tidak ditimpa (pakai --timpa bila disengaja)"], None
        except json.JSONDecodeError:
            pass
    h = urai(teks)
    koreksi = folder / "koreksi-chatgpt.md"
    if h.galat:
        koreksi.write_text(pesan_koreksi(h.galat), encoding="utf-8")
        return 1, [str(g) for g in h.galat], h
    koreksi.unlink(missing_ok=True)
    tujuan.write_text(json.dumps(h.naskah, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0, [f"naskah.json dibuat ({len(h.naskah['ketukan'])} ketukan)"], h


def main(argv: list[str]) -> int:
    pos = [a for a in argv if not a.startswith("--")]
    if not pos:
        print(__doc__)
        return 2
    kode, keluar, _ = proses(Path(pos[0]), Path(pos[1]) if len(pos) > 1 else None, "--timpa" in argv)
    print("\n".join(keluar))
    return kode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
