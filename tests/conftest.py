

import pytest as _pytest


@_pytest.fixture(autouse=True)
def _profil_ata_untuk_contoh_lama(monkeypatch):
    """Sebagian besar fixture (contoh/tenggat-planning-fallacy) ditulis untuk profil 'ata' (era lama, ATA dan KARTU).
    Test profil 'filosofi' (bawaan sekarang) menimpa ini sendiri atau memanggil monkeypatch.undo()."""
    from scripts import naskah_format
    monkeypatch.setattr(naskah_format, "profil", lambda: {"wajib_kartu": True, "maskot": "Ata"})
