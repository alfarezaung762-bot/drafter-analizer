"""Membangkitkan dua naskah uji beserta kunci jawabannya.

Gunanya satu: memberi penelaah naskah yang kesalahannya SUDAH DIKETAHUI, supaya
bisa dibuka di Word lalu dicocokkan — mana yang benar-benar tertangkap Fase 1,
dan mana yang lolos.

    python tools/buat_contoh_uji.py

Menghasilkan tiga berkas di tools/contoh/:

    uji-pmk-lengkap.docx    naskah PMK, paragraf biasa
    uji-kmk-lengkap.docx    naskah KMK, pembukaannya di dalam TABEL
    KUNCI-UJI.md            kunci jawaban

KENAPA DIBANGKITKAN, BUKAN DITULIS TANGAN
-----------------------------------------
Kunci jawaban dan naskahnya harus selalu cocok. Dua berkas yang disamakan
manual setiap kali salah satunya berubah adalah pabrik cacat — itu alasan
`docs/kontrak-data.md` dihapus, dan alasan yang sama berlaku di sini.

Karena itu keduanya lahir dari satu daftar `BLOK` di bawah, dan kuncinya tidak
cuma memuat RENCANA (apa yang seharusnya tertangkap) melainkan juga HASIL
NYATA — skrip ini menjalankan `jalankan_semua()` terhadap naskah yang baru saja
dibuatnya, lalu mencetak apa yang benar-benar keluar hari ini. Kalau aturannya
berubah, jalankan ulang skripnya dan kuncinya ikut benar dengan sendirinya.

CATATAN: naskah ini BUKAN rancangan sungguhan. Isinya karangan yang sengaja
dirusak. Jangan dipakai sebagai contoh cara menyusun PMK/KMK.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    print("python-docx belum terpasang. Jalankan:  pip install python-docx")
    raise SystemExit(1)

from app.models.temuan import JenisDokumen, ParagrafInput
from app.rules.format_baku import jalankan_semua

FOLDER = Path(__file__).resolve().parent / "contoh"


# ---------------------------------------------------------------------------
# Bentuk data satu baris naskah
# ---------------------------------------------------------------------------
#
# harap: kode aturan yang SEHARUSNYA menangkap baris ini, atau None kalau baris
#        ini justru harus DIBIARKAN. Baris ber-`harap=None` yang punya `kenapa`
#        adalah KONTROL NEGATIF — jebakan yang sengaja dipasang untuk menguji
#        bahwa alat tidak salah tandai.

class Baris:
    def __init__(self, teks: str, harap: str | None = None, kenapa: str = ""):
        self.teks = teks
        self.harap = harap
        self.kenapa = kenapa


def B(teks: str, harap: str | None = None, kenapa: str = "") -> Baris:
    return Baris(teks, harap, kenapa)


# ---------------------------------------------------------------------------
# Naskah 1 — PMK, paragraf biasa
# ---------------------------------------------------------------------------

PMK: list[Baris] = [
    B("PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA"),
    B("NOMOR 12 TAHUN 2026"),
    B("TENTANG"),
    B("PERUBAHAN ATAS PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA"),
    B("NOMOR 5 TAHUN 2023 TENTANG TATA CARA PENYUSUNAN STANDAR BIAYA MASUKAN.",
      "F1-006", "judul peraturan diakhiri tanda baca titik (butir 8)"),
    B("DENGAN RAHMAT TUHAN YANG MAHA ESA"),
    B("MENTERI KEUANGAN REPUBLIK INDONESIA,"),
    B(""),
    B("MENIMBANG :",
      "F1-007", "kata \"Menimbang\" ditulis kapital seluruhnya (butir 16)"),
    B("a. untuk melaksanakan ketentuan Pasal 12 ayat (3) Peraturan Pemerintah "
      "Nomor 45 Tahun 2013 tentang Tata Cara Pelaksanaan Anggaran;",
      "F1-008", "butir Menimbang tidak diawali kata \"bahwa\" (butir 21)"),
    B("b. bahwa standar biaya masukan perlu disesuaikan dengan perkembangan "
      "harga pasar dan kebutuhan penyelenggaraan pemerintahan.",
      "F1-008", "butir Menimbang diakhiri titik, bukan titik koma (butir 21)"),
    B("c. bahwa berdasarkan hal tersebut di atas, perlu menetapkan Peraturan "
      "Menteri Keuangan tentang Perubahan Standar Biaya Masukan;",
      "F1-004", "butir terakhir tidak memakai frasa \"sebagaimana dimaksud "
                "dalam huruf\" (butir 22)"),
    B(""),
    B("MENGINGAT :",
      "F1-009", "kata \"Mengingat\" ditulis kapital seluruhnya (butir 23)"),
    B("1. Undang-undang Nomor 17 Tahun 2003 tentang Keuangan Negara (Lembaran "
      "Negara Republik Indonesia Tahun 2003 Nomor 47);",
      "F1-005", "\"Undang-undang\" — kedua huruf u wajib kapital (butir 33)"),
    B("2. Peraturan Pemerintah Nomor 45 Tahun 2013 Tentang Tata Cara "
      "Pelaksanaan Anggaran Pendapatan dan Belanja Negara;",
      "F1-005", "kata \"Tentang\" pada dasar hukum wajib huruf kecil (butir 32)"),
    B("3. Peraturan Presiden Nomor 57 Tahun 2020 tentang Kementerian Keuangan",
      "F1-010", "dasar hukum tidak diakhiri titik koma (butir 31)"),
    B(""),
    B("M E M U T U S K A N :",
      None, "KONTROL — bentuk berspasi huruf. Kalau penanda ini tidak dikenali, "
            "F1-002, F1-011, dan F1-012 ikut mati diam-diam"),
    B(""),
    B("MENETAPKAN :",
      "F1-011", "kata \"Menetapkan\" ditulis kapital seluruhnya (butir 38)"),
    B("PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA TENTANG PERUBAHAN ATAS "
      "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA NOMOR 5 TAHUN 2023 "
      "TENTANG TATA CARA PENETAPAN STANDAR BIAYA MASUKAN",
      "F1-012", "tiga hal sekaligus di satu baris — lihat kunci di bawah"),
    B(""),
    B("Pasal 1"),
    B("Ketentuan mengenai standar biaya masukan sebagaimana dimaksud dalam "
      "Pasal 2 dilaksanakan sesuai dengan undang-undang yang mengatur mengenai "
      "keuangan negara.",
      None, "KONTROL — \"undang-undang\" generik di batang tubuh. Bukan dasar "
            "hukum, jadi butir 33 tidak berlaku dan tidak boleh ditandai"),
    B(""),
    B("Pasal 2"),
    B("Menetapkan besaran standar biaya masukan sebagaimana dimaksud dalam "
      "Pasal 1 dilakukan oleh Direktur Jenderal Anggaran.",
      None, "KONTROL — paragraf batang tubuh yang diawali kata \"Menetapkan\". "
            "Di luar jendela klausul Menetapkan, jadi bukan label bagian"),
]


# ---------------------------------------------------------------------------
# Naskah 2 — KMK, pembukaannya di dalam TABEL
# ---------------------------------------------------------------------------
#
# Bentuk bertabel itu yang dipakai naskah sungguhan, dan yang paling sering
# membuat aturan salah tandai: label dan isinya jatuh di sel — dan karenanya di
# paragraf — yang berbeda.

KMK_JUDUL: list[Baris] = [
    B("KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA"),
    B("NOMOR 88/KMK.01/2026"),
    B("TENTANG"),
    B("PENETAPAN PEJABAT PENGELOLA KEUANGAN DI LINGKUNGAN SEKRETARIAT JENDERAL"),
    B("MENTERI KEUANGAN REPUBLIK INDONESIA,"),
]

# (label, isi) tiap baris tabel pembukaan
KMK_TABEL: list[tuple[Baris, list[Baris]]] = [
    (B("Menimbang",
       None, "KONTROL — label berdiri sendiri di selnya, titik duanya ada di "
             "sel sebelah. Tidak bisa dibuktikan hilang, jadi F1-007 harus DIAM"),
     [B("a. bahwa dalam rangka tertib administrasi pengelolaan keuangan "
        "negara perlu ditetapkan pejabat pengelola keuangan;"),
      B("b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, "
        "perlu menetapkan Peraturan Menteri Keuangan tentang Penetapan "
        "Pejabat Pengelola Keuangan;",
        "F1-004", "naskah KMK tetapi menyebut \"Peraturan Menteri Keuangan\"; "
                  "butir 22 menuntut \"Keputusan Menteri Keuangan\". INILAH "
                  "yang membuat pilihan PMK/KMK di panel wajib")]),
    (B("Mengingat",
       None, "KONTROL — sama dengan Menimbang, F1-009 harus DIAM"),
     [B("1. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara;"),
      B("2. Peraturan Menteri Keuangan Nomor 202/PMK.010/2017 tentang Tata "
        "Cara Pengelolaan Keuangan;",
        None, "KONTROL — penyebutan \"Peraturan Menteri Keuangan\" di dasar "
              "hukum sebuah KMK. Dulu jenis dokumen ditebak dari penyebutan "
              "pertama, dan naskah seperti ini dikira PMK")]),
]

KMK_DIKTUM: list[Baris] = [
    B("M E M U T U S K A N :"),
    B(""),
]

# (label diktum, isinya) — dipisah paragraf, seperti naskah bertabel
KMK_ISI_DIKTUM: list[tuple[Baris, Baris]] = [
    (B("Menetapkan"),
     B("KEPUTUSAN MENTERI KEUANGAN TENTANG PENETAPAN PEJABAT PENGELOLA "
       "KEUANGAN DI LINGKUNGAN SEKRETARIAT JENDERAL.")),
    (B("KESATU"),
     B("Menetapkan pejabat pengelola keuangan di lingkungan Sekretariat "
       "Jenderal sebagaimana tercantum dalam Lampiran yang merupakan bagian "
       "tidak terpisahkan dari Keputusan Menteri ini.",
       None, "KONTROL — isi diktum KMK yang diawali kata \"Menetapkan\". "
             "Inilah salah tandai yang ditemukan 18 Sep 2026 (6.10 Kasus 6): "
             "F1-011 menuduh batang tubuh ini kurang titik dua")),
    (B("KEDUA"),
     B("Keputusan Menteri ini mulai berlaku pada tanggal ditetapkan.")),
]


# ---------------------------------------------------------------------------
# Pembangkit dokumen
# ---------------------------------------------------------------------------

def _tulis(doc, teks: str, tengah: bool = False) -> None:
    p = doc.add_paragraph(teks)
    if tengah:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER


def buat_pmk(path: Path) -> list[Baris]:
    doc = Document()
    for i, b in enumerate(PMK):
        _tulis(doc, b.teks, tengah=i < 7)
    doc.save(str(path))
    return PMK


def buat_kmk(path: Path) -> list[Baris]:
    """KMK dengan pembukaan di dalam tabel — bentuk naskah sungguhan."""
    doc = Document()
    urut: list[Baris] = []

    for b in KMK_JUDUL:
        _tulis(doc, b.teks, tengah=True)
        urut.append(b)
    _tulis(doc, "")
    urut.append(B(""))

    tabel = doc.add_table(rows=0, cols=2)
    for label, isi_list in KMK_TABEL:
        baris = tabel.add_row()
        baris.cells[0].text = label.teks
        baris.cells[1].text = isi_list[0].teks
        urut.append(label)
        urut.append(isi_list[0])
        for lanjut in isi_list[1:]:
            baris2 = tabel.add_row()
            baris2.cells[0].text = ""
            baris2.cells[1].text = lanjut.teks
            urut.append(B(""))
            urut.append(lanjut)

    for b in KMK_DIKTUM:
        _tulis(doc, b.teks, tengah=True)
        urut.append(b)

    tabel2 = doc.add_table(rows=0, cols=2)
    for label, isi in KMK_ISI_DIKTUM:
        baris = tabel2.add_row()
        baris.cells[0].text = label.teks
        baris.cells[1].text = isi.teks
        urut.append(label)
        urut.append(isi)

    doc.save(str(path))
    return urut


# ---------------------------------------------------------------------------
# Kunci jawaban
# ---------------------------------------------------------------------------

def _paragraf_dari(path: Path) -> list[ParagrafInput]:
    """Baca ulang .docx yang baru dibuat, persis seperti cek_docx.py membacanya."""
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(str(path))
    teks: list[str] = []
    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            teks.append(Paragraph(child, doc).text)
        elif child.tag == qn("w:tbl"):
            for baris in Table(child, doc).rows:
                for sel in baris.cells:
                    for p in sel.paragraphs:
                        teks.append(p.text)
    return [ParagrafInput(index=i, teks=t) for i, t in enumerate(teks)]


def _bagian_rencana(judul: str, baris: list[Baris]) -> list[str]:
    salah = [b for b in baris if b.harap]
    kontrol = [b for b in baris if not b.harap and b.kenapa]

    out = [f"### {judul} — yang sengaja dirusak", ""]
    out += ["| Aturan | Kesalahannya | Cuplikan |", "|---|---|---|"]
    for b in salah:
        cuplik = b.teks[:52] + ("…" if len(b.teks) > 52 else "")
        out.append(f"| {b.harap} | {b.kenapa} | `{cuplik}` |")
    out += ["", f"### {judul} — jebakan yang TIDAK boleh ditandai", ""]
    out += ["| Kenapa dipasang | Cuplikan |", "|---|---|"]
    for b in kontrol:
        cuplik = b.teks[:52] + ("…" if len(b.teks) > 52 else "")
        out.append(f"| {b.kenapa} | `{cuplik}` |")
    out.append("")
    return out


def _bagian_hasil(judul: str, path: Path, jenis: JenisDokumen) -> list[str]:
    paragraf = _paragraf_dari(path)
    temuan = jalankan_semua(paragraf, jenis)

    out = [f"### {judul} — hasil NYATA hari ini", ""]
    out.append(f"Dijalankan terhadap `{path.name}` sebagai **{jenis.value}**, "
               f"seluruh aturan menyala. Keluar **{len(temuan)} temuan**.")
    out += ["", "| # | Aturan | Jenis | Par | Yang ditandai |", "|---|---|---|---|---|"]
    for t in temuan:
        asli = t.lokasi.teks_asli.strip()
        cuplik = (asli[:40] + "…") if len(asli) > 40 else asli
        if not cuplik:
            cuplik = "_(tanpa lokasi — jadi peringatan dokumen)_"
        else:
            cuplik = f"`{cuplik}`"
        out.append(
            f"| T{t.nomor} | {t.aturan_id} | {t.jenis_tanda.value} | "
            f"{t.lokasi.paragraf_index} | {cuplik} |"
        )
    out.append("")
    return out


def tulis_kunci(path: Path, pmk_path: Path, kmk_path: Path,
                pmk_baris: list[Baris], kmk_baris: list[Baris]) -> None:
    out = [
        "# Kunci naskah uji Fase 1",
        "",
        "> **Dibangkitkan otomatis oleh `tools/buat_contoh_uji.py`. Jangan "
        "disunting tangan** — jalankan ulang skripnya, dan berkas ini ikut "
        "benar dengan sendirinya. Naskahnya karangan yang sengaja dirusak, "
        "bukan rancangan sungguhan.",
        "",
        "Dua naskah, dua bentuk yang berbeda:",
        "",
        "| Berkas | Bentuk | Gunanya |",
        "|---|---|---|",
        f"| `{pmk_path.name}` | paragraf biasa | menguji sebagian besar aturan "
        "sekaligus |",
        f"| `{kmk_path.name}` | pembukaan di dalam **tabel** | bentuk naskah "
        "sungguhan, dan yang paling sering membuat aturan salah tandai |",
        "",
        "## Cara memakainya",
        "",
        "```bash",
        "# tanpa membuka Word",
        f"cd backend && python tools/cek_docx.py tools/contoh/{pmk_path.name} --jenis PMK",
        f"cd backend && python tools/cek_docx.py tools/contoh/{kmk_path.name} --jenis KMK",
        "```",
        "",
        "Lalu buka berkasnya di Word lewat add-in, pilih jenis dokumennya, dan "
        "cocokkan dengan tabel di bawah.",
        "",
        "**Dua hal yang layak dicoba juga:**",
        "",
        f"1. Buka `{kmk_path.name}` lalu pilih **PMK** (jenis yang salah). "
        "Temuan F1-004 akan berubah bunyinya — itu memperlihatkan kenapa "
        "pilihan jenis dokumen dibuat wajib dan tanpa nilai awal.",
        "2. Warnai satu kata dengan warna biru sebelum menganalisis, lalu tekan "
        "**Bersihkan Daftar**. Warna itu harus tetap biru — alat hanya boleh "
        "mencabut warnanya sendiri.",
        "",
        "## Yang BELUM bisa diuji dari kedua berkas ini",
        "",
        "**F1-003 (kelengkapan Menimbang / Mengingat / Menetapkan).** Menguji "
        "aturan ini menuntut salah satu bagian itu DIHAPUS — dan begitu "
        "dihapus, hampir seluruh aturan lain ikut kehilangan jangkarnya lalu "
        "memilih diam. Cara mengujinya: buka salah satu berkas di Word, hapus "
        "baris `Mengingat`, lalu jalankan analisis. Hasil yang benar: muncul "
        "peringatan dokumen berlatar merah muda di atas daftar, **bukan** "
        "kartu temuan — karena ketiadaan sebuah bagian tidak punya lokasi "
        "untuk ditunjuk.",
        "",
        "---",
        "",
    ]
    out += _bagian_rencana("Naskah PMK", pmk_baris)
    out += _bagian_hasil("Naskah PMK", pmk_path, JenisDokumen.PMK)
    out += ["---", ""]
    out += _bagian_rencana("Naskah KMK", kmk_baris)
    out += _bagian_hasil("Naskah KMK", kmk_path, JenisDokumen.KMK)
    out += [
        "---",
        "",
        "## Cara membaca selisihnya",
        "",
        "Bandingkan tabel **yang sengaja dirusak** dengan tabel **hasil "
        "nyata**. Tiga kemungkinan, dan ketiganya berguna:",
        "",
        "- **Ada di keduanya** — aturannya bekerja.",
        "- **Ada di rencana, tidak ada di hasil** — aturannya diam. Belum tentu "
        "cacat: bisa jadi ia memang memilih diam karena tidak bisa "
        "membuktikan kesalahannya. Periksa alasannya di panel Pengaturan, "
        "bagian \"Yang TIDAK diperiksa\".",
        "- **Ada di hasil, tidak ada di rencana** — ini yang paling penting. "
        "Berarti alat menandai sesuatu yang tidak sengaja dirusak. Periksa "
        "naskahnya: kalau memang tidak salah, itu **salah tandai** dan wajib "
        "dilaporkan.",
        "",
        "Satu baris bisa memuat lebih dari satu kesalahan, jadi jumlah temuan "
        "boleh lebih banyak daripada jumlah baris di tabel rencana.",
        "",
    ]
    path.write_text("\n".join(out), encoding="utf-8")


def main() -> None:
    FOLDER.mkdir(parents=True, exist_ok=True)
    pmk_path = FOLDER / "uji-pmk-lengkap.docx"
    kmk_path = FOLDER / "uji-kmk-lengkap.docx"
    kunci_path = FOLDER / "KUNCI-UJI.md"

    pmk_baris = buat_pmk(pmk_path)
    kmk_baris = buat_kmk(kmk_path)
    tulis_kunci(kunci_path, pmk_path, kmk_path, pmk_baris, kmk_baris)

    for p in (pmk_path, kmk_path, kunci_path):
        print(f"  dibuat: {p.relative_to(FOLDER.parent.parent)}")


if __name__ == "__main__":
    main()
