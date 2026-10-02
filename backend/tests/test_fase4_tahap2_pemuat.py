"""Fase 4 — pemuat analisis.md/analisisformat.md/skills: menolak formulir cacat, memilih.

Formulir cacat membuat backend MENOLAK MENYALA dan menyebut analisisnya —
tidak pernah dilewati diam-diam (rancangan Fase 4 bagian 5.1).
"""

from pathlib import Path

import pytest

from app.telaah.tahap2_agen.langkah1_pilih_analisis import (
    FormulirCacat,
    Prasyarat,
    daftar_panel,
    muat_katalog,
    pilih,
)

BAGIAN_BAIK = """## X-01 · Analisis uji

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: per pasal
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf C butir 54 huruf a, hlm 39 (visual)
Butuh: —

### Yang diperiksa
- sesuatu

### Yang tidak diperiksa
- yang lain

### Cara memeriksa
Baca.
"""

FORMAT_BAIK = """## X-02 · Format uji

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: format
Dasar: prioritas penelaah

### Yang diperiksa
- format
"""

SKILL = "---\nname: {nama}\ndescription: uji\n---\n\nKaidah.\n"


def _folder(tmp_path: Path, isi: str = BAGIAN_BAIK, format_: str = FORMAT_BAIK, skill_label: bool = True) -> Path:
    a = tmp_path / "analisis"
    a.mkdir(parents=True)
    (a / "analisis.md").write_text("# Analisis\n\n" + isi, encoding="utf-8")
    (a / "analisisformat.md").write_text(format_, encoding="utf-8")
    (a / "_TEMPLATE.md").write_text("## Kode · Judul\n\nRespons: ngawur\n", encoding="utf-8")
    for nama in (["pmk-standar/label"] if skill_label else []) + ["pmk-standar/pembukaan", "korpus"]:
        d = tmp_path / nama
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(SKILL.format(nama=nama), encoding="utf-8")
    return tmp_path


class TestKatalogNyata:
    def test_analisis_dan_skill_proyek_terbaca_tanpa_cacat(self):
        k = muat_katalog()
        kode = [a.kode for a in k.analisis]
        assert len(kode) == len(set(kode))
        # Pemeriksaan yang sudah ada dipindah semua, ditambah empat analisis baru.
        for wajib in (
            "F1-002", "F1-003", "F1-004", "F1-005", "F1-006", "F1-007", "F1-008",
            "F1-009", "F1-010", "F1-011", "F1-012", "F2-001", "F2-003", "F2-004",
            "F2-007", "F2-101", "F2-102", "F2-103", "F2-104", "F2-105", "F2-106",
            "F3-001", "F3-002", "F3-003", "I-37", "S-64", "F-19", "F-20",
        ):
            assert wajib in kode, wajib
        # F1-001 tetap dimatikan — bacaan kapital dari gaya belum terbukti.
        assert "F1-001" not in kode
        assert "pmk-standar/label" in k.skill and "korpus" in k.skill

    def test_template_tidak_dimuat_sebagai_analisis(self):
        assert all(a.kode != "Kode" for a in muat_katalog().analisis)

    def test_analisis_format_hanya_di_berkas_format(self):
        for a in muat_katalog().analisis:
            assert (a.lingkup == "format") == (a.berkas == "analisisformat.md")


class TestMenolakFormulirCacat:
    @pytest.mark.parametrize(
        "ganti, pesan",
        [
            (("Respons: catatan", "Respons: hijau"), "Respons"),
            (("Lingkup: per pasal", "Lingkup: sepasal"), "Lingkup"),
            (("Respons: catatan\n", ""), "'Respons' wajib diisi"),
            (("Komentar: lengkap", "Komentar: panjang"), "Komentar"),
            (("Butuh: —", "Butuh: internet"), "Butuh"),
            (("hlm 39 (visual)", "hlm 39"), "Dasar"),
            (("- sesuatu", ""), "Yang diperiksa"),
            (("Berlaku untuk: pmk-standar", "Berlaku untuk: PMK Standar"), "jenis naskah"),
            (("### Cara memeriksa", "### Cara lain"), "subbagian tidak dikenal"),
            (("Butuh: —", "Butuh: —\nTambahan: x"), "baris kepala tidak dikenal"),
        ],
    )
    def test_nilai_di_luar_pilihan_menghentikan_backend(self, tmp_path, ganti, pesan):
        lama, baru = ganti
        folder = _folder(tmp_path, BAGIAN_BAIK.replace(lama, baru, 1))
        with pytest.raises(FormulirCacat) as e:
            muat_katalog(folder)
        assert pesan in str(e.value)
        assert "X-01" in str(e.value)  # menyebut analisisnya

    def test_kode_kembar_ditolak(self, tmp_path):
        folder = _folder(tmp_path, BAGIAN_BAIK + "\n" + BAGIAN_BAIK)
        with pytest.raises(FormulirCacat, match="kembar"):
            muat_katalog(folder)

    def test_lingkup_format_di_analisis_md_ditolak(self, tmp_path):
        folder = _folder(tmp_path, BAGIAN_BAIK.replace("Lingkup: per pasal", "Lingkup: format"))
        with pytest.raises(FormulirCacat, match="analisisformat.md"):
            muat_katalog(folder)

    def test_skill_tanpa_nama_yang_cocok_ditolak(self, tmp_path):
        folder = _folder(tmp_path)
        (folder / "korpus" / "SKILL.md").write_text("---\nname: lain\ndescription: x\n---\nisi", encoding="utf-8")
        with pytest.raises(FormulirCacat, match="name"):
            muat_katalog(folder)

    def test_formulir_baik_terbaca(self, tmp_path):
        k = muat_katalog(_folder(tmp_path))
        a = k.cari("X-01")
        assert a.respons == "catatan" and a.lingkup == "per pasal"
        assert a.dasar.startswith("Lampiran II") and a.dasar_status == "visual"
        assert a.diperiksa == ["sesuatu"] and a.butuh == []
        assert k.cari("X-02").dasar_status == "prioritas"


class TestMemilih:
    def test_jenis_lain_belum_tersedia(self, tmp_path):
        k = muat_katalog(_folder(tmp_path))
        p = pilih(k, "kmk")
        assert not p.dikirim
        assert ("X-01", "belum tersedia untuk KMK") in p.tidak_dikirim

    def test_tanpa_skill_label_jenis_itu_tidak_dikirim(self, tmp_path):
        k = muat_katalog(_folder(tmp_path, skill_label=False))
        assert not pilih(k, "pmk-standar").dikirim

    def test_butuh_korpus_tanpa_korpus_disebut_alasannya(self, tmp_path):
        k = muat_katalog(_folder(tmp_path, BAGIAN_BAIK.replace("Butuh: —", "Butuh: korpus")))
        p = pilih(k, "pmk-standar", prasyarat=Prasyarat(korpus=False))
        assert ("X-01", "korpus tidak terhubung") in p.tidak_dikirim
        assert pilih(k, "pmk-standar", prasyarat=Prasyarat(korpus=True)).dikirim

    def test_yang_dimatikan_penelaah_tidak_disebut(self, tmp_path):
        k = muat_katalog(_folder(tmp_path))
        p = pilih(k, "pmk-standar", ["X-02"])
        assert [a.kode for a in p.dikirim] == ["X-02"]
        assert p.tidak_dikirim == []

    def test_daftar_panel_berbentuk_daftar_lama(self, tmp_path):
        d = daftar_panel(muat_katalog(_folder(tmp_path)), "pmk-standar")
        x = next(a for a in d if a["id"] == "X-01")
        assert x["judul"] == "Analisis uji" and x["diperiksa"] == ["sesuatu"]
        assert x["tidakDiperiksa"] == ["yang lain"] and x["tersedia"] is True
