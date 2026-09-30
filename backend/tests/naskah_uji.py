"""Naskah uji bersama untuk tes tahap 1–5 — kecil, tetapi berlampiran dan bertabel.

Bentuknya meniru naskah nyata di `tools/contoh/tempat pmk/`: lampiran berangka
Romawi, kepala lampiran di baris-baris sendiri, tabel data di lampiran, dan
blok penutup pejabat di akhir tiap lampiran.
"""

from app.models.temuan import ParagrafInput

PEMBUKAAN = [
    "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
    "NOMOR 12 TAHUN 2026",
    "TENTANG",
    "TATA CARA PENETAPAN STATUS PENGGUNAAN",
    "DENGAN RAHMAT TUHAN YANG MAHA ESA",
    "MENTERI KEUANGAN REPUBLIK INDONESIA,",
    "Menimbang :",
    "a. bahwa untuk tertib pengelolaan barang perlu menetapkan Peraturan Menteri;",
    "Mengingat :",
    "1. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara;",
    "MEMUTUSKAN:",
    "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA PENETAPAN STATUS PENGGUNAAN.",
]

BATANG = [
    "Pasal 1",
    "Dalam Peraturan Menteri ini yang dimaksud dengan:",
    "1. Pengelola Barang adalah pejabat yang berwenang menetapkan status penggunaan.",
    "2. Pengguna Barang adalah pejabat pemegang kewenangan penggunaan barang.",
    "Pasal 2",
    "Pengguna Barang wajib mengajukan permohonan paling lambat 30 (tiga puluh) hari.",
    "Pasal 3",
    "Daftar barang tercantum dalam Lampiran I yang merupakan bagian tidak "
    "terpisahkan dari Peraturan Menteri ini.",
    "Pasal 4",
    "Peraturan Menteri ini mulai berlaku pada tanggal diundangkan.",
]

PENUTUP = [
    "Ditetapkan di Jakarta",
    "pada tanggal 2 Januari 2026",
    "MENTERI KEUANGAN REPUBLIK INDONESIA,",
    "ttd.",
    "NAMA MENTERI",
]

KEPALA_LAMPIRAN_I = [
    "LAMPIRAN I",
    "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
    "NOMOR 12 TAHUN 2026",
    "TENTANG",
    "TATA CARA PENETAPAN STATUS PENGGUNAAN",
    "DAFTAR BARANG",
]

KEPALA_LAMPIRAN_II = [
    "LAMPIRAN II",
    "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
    "NOMOR 12 TAHUN 2026",
    "TENTANG",
    "TATA CARA PENETAPAN STATUS PENGGUNAAN",
    "CONTOH FORMAT SURAT",
    "Lampiran Surat",
    "Nomor : ....",
    "Isi surat permohonan.",
]

PENUTUP_LAMPIRAN = ["MENTERI KEUANGAN REPUBLIK INDONESIA,", "ttd.", "NAMA MENTERI"]


def teks(baris: list[str]) -> list[ParagrafInput]:
    return [ParagrafInput(index=0, teks=t) for t in baris]


def tabel(isi: list[list[str]], nomor: int) -> list[ParagrafInput]:
    """Satu paragraf per sel, berurutan seperti body.paragraphs di Word."""
    return [
        ParagrafInput(index=0, teks=t, tabel=nomor, baris=b, sel=s)
        for b, sel in enumerate(isi)
        for s, t in enumerate(sel)
    ]


def nomori(paragraf: list[ParagrafInput]) -> list[ParagrafInput]:
    return [p.model_copy(update={"index": i}) for i, p in enumerate(paragraf)]


def data_barang(nomor: int, jumlah: int = 6) -> list[ParagrafInput]:
    """Tabel data "NO. | NAMA BARANG | JUMLAH" — sejenis antar-nomor tabel."""
    isi = [["NO.", "NAMA BARANG", "JUMLAH"]]
    isi += [[f"{i}.", f"Barang {nomor}-{i}", f"{i}.000"] for i in range(1, jumlah + 1)]
    return tabel(isi, nomor)


def naskah(
    batang: list[str] | None = None,
    lampiran: bool = True,
    tabel_lampiran: list[list[ParagrafInput]] | None = None,
) -> list[ParagrafInput]:
    """Naskah lengkap. Bawaannya: dua lampiran, Lampiran I memuat satu tabel data."""
    isi = teks(PEMBUKAAN + (batang if batang is not None else BATANG) + PENUTUP)
    if lampiran:
        isi += teks(KEPALA_LAMPIRAN_I)
        for t in tabel_lampiran if tabel_lampiran is not None else [data_barang(0)]:
            isi += t
        isi += teks(PENUTUP_LAMPIRAN)
        isi += teks(KEPALA_LAMPIRAN_II + PENUTUP_LAMPIRAN)
    return nomori(isi)
