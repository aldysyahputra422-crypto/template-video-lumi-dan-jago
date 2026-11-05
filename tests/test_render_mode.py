from scripts import render


def test_motion_blur_render_dua_kali_lalu_campur():
    sumber, vf = render.saring(30, True)
    assert sumber == 60 and vf.startswith("tmix=frames=2") and "fps=30" in vf and render.GRAIN in vf
    assert render.saring(30, False) == (30, render.GRAIN)


def test_mode_kualitas_aktif_di_konfigurasi():
    assert render.mode().get("motion_blur") is True
