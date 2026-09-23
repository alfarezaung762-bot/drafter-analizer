"""Alat bantu sekali pakai — BUKAN bagian produk, tidak ikut ke add-in.

Membaca rancangan PMK/KMK berformat .docx, menampilkan daftar paragrafnya apa
adanya, lalu menjalankan seluruh aturan Fase 1 terhadap paragraf itu.

Gunanya menjawab satu pertanyaan yang belum pernah diukur dari naskah nyata:
bagaimana Word sebenarnya memecah blok Menimbang menjadi paragraf. Selama itu
belum diketahui, seluruh tes yang ada masih memakai dokumen buatan sendiri yang
jauh lebih rapi daripada rancangan sungguhan.

Catatan penting soal tabel: di banyak rancangan, blok "Menimbang" dan
"Mengingat" ditata memakai TABEL, bukan tab. Skrip ini menelusuri isi tabel
juga dan menandainya, karena kalau ternyata begitu, cara parser membaca dokumen
perlu ditinjau ulang.

Pakai:
    python tools/cek_docx.py "path/ke/rancangan.docx"
    python tools/cek_docx.py "path/ke/rancangan.docx" --paragraf-saja
    python tools/cek_docx.py "path/ke/rancangan.docx" --batas 40

Tidak perlu server backend menyala — aturannya dipanggil langsung.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Supaya bisa dijalankan dari folder backend/ tanpa dipasang sebagai paket
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph
except ImportError:
    print("python-docx belum terpasang. Jalankan:  pip install python-docx")
    raise SystemExit(1)

from tools.penomoran import Penomoran

from app.models.temuan import JenisDokumen, ParagrafInput
from app.rules.format_baku import jalankan_semua
from app.fase2.tahap0_struktur import bangun_pohon
from app.fase2.tahap0_definisi import ambil_definisi
from app.fase2.tahap1_saring import saring
from app.fase2.mekanis_konsistensi import jalankan_mekanis


def baca_paragraf(path: Path) -> list[dict]:
    """Baca seluruh paragraf dokumen menurut urutan asli, termasuk isi tabel.

    Tiap entri: {'teks': str, 'penanda': str, 'tingkat': int, 'dari_tabel': bool}

    `penanda` adalah nomor otomatis Word — "Pasal 5", "(2)", "a." — yang TIDAK
    ikut di `paragraph.text` dan karena itu harus dihitung sendiri. Pada naskah
    PMK sungguhan 60% paragrafnya bernomor otomatis, jadi tanpa ini alat
    diagnosa membaca naskah yang berbeda dari yang dibaca add-in.

    Penghitungnya CERMINAN Word, bukan Word — batasnya di tools/penomoran.py.
    """
    doc = Document(str(path))
    nomor = Penomoran(doc)
    hasil: list[dict] = []

    def tambah(p, dari_tabel: bool) -> None:
        penanda, tingkat = nomor.berikutnya(p)
        hasil.append(
            {
                "teks": p.text,
                "penanda": penanda,
                "tingkat": tingkat,
                "dari_tabel": dari_tabel,
            }
        )

    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            tambah(Paragraph(child, doc), False)
        elif child.tag == qn("w:tbl"):
            tabel = Table(child, doc)
            for baris in tabel.rows:
                for sel in baris.cells:
                    for p in sel.paragraphs:
                        tambah(p, True)

    return hasil


def _cetak_temuan(temuan) -> None:
    """Cetak daftar temuan berikut rentang persis yang akan ditandai di Word."""
    print("=" * 78)
    print(f"TEMUAN : {len(temuan)}")
    print("=" * 78)
    for t in temuan:
        print()
        print(f"T{t.nomor:<3} [{t.jenis_tanda.value:<12}] {t.aturan_id}  paragraf #{t.lokasi.paragraf_index}")
        # Rentang yang benar-benar ditandai di Word. Dicetak supaya bisa dilihat
        # apakah yang tersorot memang sesempit yang dimaksud, bukan satu
        # paragraf penuh.
        print(
            f"  Ditandai: [{t.lokasi.offset_mulai}:"
            f"{t.lokasi.offset_mulai + t.lokasi.panjang}] "
            f"{t.lokasi.teks_asli!r}"
        )
        print(f"  Temuan  : {t.catatan}")
        # Saran punya medan sendiri sejak 22 Sep 2026. Menyembunyikannya di
        # sini membuat alat diagnosa memperlihatkan separuh dari yang akan
        # dibaca penelaah di komentar Word.
        if getattr(t, "saran", ""):
            print(f"  Saran   : {t.saran}")
        if t.usulan_rumusan:
            # Hanya terisi pada temuan HIJAU — yang benar-benar disisipkan.
            print(f"  Disisipkan hijau: {t.usulan_rumusan}")
        # Yang menentukan status, BUKAN keterisian butirnya. Butir yang sudah
        # terisi dari ekstraksi OCR tetap belum diverifikasi siapa pun.
        butir = t.rujukan.butir
        status = t.rujukan.status
        if status == "visual":
            print(f"  Rujukan : {t.rujukan.sumber} butir {butir}")
        elif status == "ekstraksi":
            print(
                f"  Rujukan : {t.rujukan.sumber} butir {butir} "
                "— BELUM DIVERIFIKASI VISUAL (isi dari ekstraksi OCR)"
            )
        else:
            print("  Rujukan : BELUM DIISI — butir dan kutipannya masih placeholder")


def _jalankan_lanjut(paragraf, args) -> int:
    """Jalankan seluruh Fase 2 (dan 3) terhadap naskah ini. MEMANGGIL MODEL.

    Ini satu-satunya cara menguji jalur penalaran tanpa membuka Word. Yang
    dicetak bukan cuma temuannya melainkan juga YANG GUGUR di Langkah 5 dan
    ongkosnya — dua angka yang menentukan apakah alat ini layak dipakai, dan
    dua-duanya tidak kelihatan dari panel.
    """
    from app.bersama.llm import KlienAzure, PerapalAzure
    from app.bersama.opensearch import KorpusOpenSearch, PencariOpenSearch
    from app.core.config import settings
    from app.fase2.alur import jalankan_lanjut

    klien = KlienAzure()
    if not klien.siap:
        print("Azure OpenAI belum terkonfigurasi. Periksa lewat GET /cek-env.")
        return 1

    korpus = perapal = pencari = None
    if args.fase3:
        korpus, perapal = KorpusOpenSearch(), PerapalAzure()
        if not (korpus.siap and perapal.siap):
            print("F3-001 diminta tetapi OpenSearch/embedding belum siap — dilewati.")
            korpus = perapal = None
        cari = PencariOpenSearch()
        pencari = cari if cari.siap else None

    def lapor(selesai: int, total: int, _baru) -> None:
        print(f"  Langkah 2: {selesai}/{total} satuan terbaca")

    print("=" * 78)
    print("FASE 2 — JALUR PENALARAN (memanggil model, berbiaya)")
    print("=" * 78)

    hasil = jalankan_lanjut(
        paragraf,
        klien=klien,
        korpus=korpus,
        perapal=perapal,
        pencari=pencari,
        ambang=args.ambang if args.ambang is not None else settings.FASE2_AMBANG_SKOR,
        per_panggilan=settings.FASE2_SATUAN_PER_PANGGILAN,
        lapor=lapor,
    )

    if not hasil.berjalan:
        print()
        print("FASE 2 TIDAK DIJALANKAN")
        print(f"  {hasil.tidak_dijalankan}")
        # F3-002 berjalan SEBELUM penjaga struktur, jadi temuannya bisa ada
        # walau Fase 2 berhenti. Menyembunyikannya di sini membuat alat
        # diagnosa berbohong tentang apa yang sebenarnya diperiksa.
        if hasil.temuan:
            print()
            _cetak_temuan(hasil.temuan)
        for g in hasil.gugur:
            print(f"  (diam) {g}")
        return 0

    print()
    print(f"  Peta    : {len(hasil.peta)} baris dari {hasil.satuan_total} satuan")
    print(f"  Dugaan  : {len(hasil.dugaan)} dari Langkah 3")
    print(f"  Ongkos  : {hasil.ongkos.ringkas()}")
    print()

    # Dicetak dari hasil yang BARU SAJA berjalan, bukan dari simpanan: peta
    # yang diperlihatkan harus peta yang dipakai, dan di CLI keduanya ada di
    # tangan sekaligus.
    if args.tahap3:
        from app.fase2.ekspor_tahap3 import susun_ekspor_tahap3

        print(
            susun_ekspor_tahap3(
                paragraf,
                hasil.peta,
                hasil.dugaan,
                dokumen=Path(args.berkas).name,
            )
        )

    _cetak_temuan(hasil.temuan)

    # Yang gugur sama pentingnya dengan yang lolos: inilah bukti Langkah 5
    # benar-benar bekerja, bukan cuma ada.
    if hasil.gugur:
        print()
        print("=" * 78)
        print(f"GUGUR DI LANGKAH 5 : {len(hasil.gugur)}")
        print("=" * 78)
        for g in hasil.gugur:
            print(f"  {g}")
    print()
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Periksa rancangan .docx dengan aturan Fase 1")
    ap.add_argument("berkas", help="Path ke rancangan .docx")
    ap.add_argument("--paragraf-saja", action="store_true", help="Hanya tampilkan paragraf, tanpa menjalankan aturan")
    ap.add_argument("--batas", type=int, default=60, help="Jumlah paragraf yang ditampilkan (default 60, 0 = semua)")
    ap.add_argument("--struktur", action="store_true", help="Tampilkan pohon satuan hasil parser Fase 2")
    ap.add_argument("--fase2", action="store_true", help="Jalankan pemeriksaan mekanis Fase 2 (F2-001..007), bukan Fase 1")
    ap.add_argument("--tahap0", action="store_true", help="ALAT PENGEMBANG: cetak apa yang akan dibaca model, termasuk satuan yang dibuang penyaring")
    ap.add_argument("--lanjut", action="store_true", help="Jalankan SELURUH Fase 2 termasuk jalur penalaran. MEMANGGIL MODEL dan BERBIAYA.")
    ap.add_argument("--fase3", action="store_true", help="Bersama --lanjut: cari pembanding di korpus peraturan (OpenSearch + embedding).")
    ap.add_argument("--tahap3", action="store_true", help="Bersama --lanjut: cetak peta Langkah 2 dan dugaan Langkah 3 yang baru saja dipakai.")
    ap.add_argument("--ambang", type=float, default=None, help="Ambang skor Langkah 5. Bawaan dari core/config.py.")
    ap.add_argument("--jenis", choices=["PMK", "KMK"], default="PMK", help="Jenis dokumen; di add-in ini dipilih penelaah (default PMK)")
    args = ap.parse_args()

    path = Path(args.berkas)
    if not path.exists():
        print(f"Berkas tidak ditemukan: {path}")
        return 1

    entri = baca_paragraf(path)
    jml_tabel = sum(1 for e in entri if e["dari_tabel"])

    print("=" * 78)
    print(f"BERKAS : {path.name}")
    print(f"PARAGRAF: {len(entri)} total, {jml_tabel} di antaranya berasal dari dalam tabel")
    if jml_tabel:
        print()
        print("  PERHATIAN: dokumen ini memakai tabel. Periksa apakah blok Menimbang/")
        print("  Mengingat termasuk di dalamnya — kalau iya, tata letaknya berbeda dari")
        print("  yang diasumsikan tes saat ini, dan parser perlu ditinjau ulang.")
    print("=" * 78)
    print()

    batas = len(entri) if args.batas == 0 else min(args.batas, len(entri))
    print(f"--- {batas} paragraf pertama (ditampilkan apa adanya, termasuk spasi/tab) ---")
    for i in range(batas):
        tanda = "[TABEL]" if entri[i]["dari_tabel"] else "       "
        pen = entri[i].get("penanda", "")
        awalan = f"{pen!r:<12}" if pen else " " * 12
        print(f"{i:>4} {tanda} {awalan} {entri[i]['teks']!r}")
    if batas < len(entri):
        print(f"     ... {len(entri) - batas} paragraf berikutnya tidak ditampilkan (pakai --batas 0 untuk semua)")
    print()

    if args.paragraf_saja:
        return 0

    paragraf = [
        ParagrafInput(
            index=i,
            teks=e["teks"],
            penanda=e.get("penanda", ""),
            tingkat=e.get("tingkat", -1),
        )
        for i, e in enumerate(entri)
    ]
    jenis = JenisDokumen(args.jenis)

    if args.tahap0:
        from app.core.config import settings
        from app.fase2.ekspor_tahap0 import susun_ekspor

        print(
            susun_ekspor(
                paragraf,
                per_panggilan=settings.FASE2_SATUAN_PER_PANGGILAN,
                dokumen=path.name,
            )
        )
        return 0

    if args.lanjut:
        return _jalankan_lanjut(paragraf, args)

    if args.struktur or args.fase2:
        pohon = bangun_pohon(paragraf)
        if args.struktur:
            print("=" * 78)
            print(f"POHON SATUAN : {len(pohon.satuan)} satuan")
            print("=" * 78)
            if pohon.gagal:
                print()
                print(f"  PARSER MELAPOR GAGAL: {pohon.gagal}")
                print()
            for s_ in pohon.satuan:
                dalam = 0 if s_.induk is None else 1 + s_.id.count("-") // 2
                isi = (s_.teks[:46] + "…") if len(s_.teks) > 46 else s_.teks
                print(
                    f"  {'  ' * dalam}{s_.id:<34} [{s_.jenis.value:<10}] "
                    f"p{s_.paragraf_mulai}-{s_.paragraf_akhir}  {isi!r}"
                )
            hs = saring(pohon)
            dibaca, dilewati = hs.jumlah
            print()
            print(f"  PENYARING LANGKAH 1: {dibaca} dibaca model, {dilewati} dilewati")
            for s_, alasan in hs.dilewati:
                print(f"    dilewati  {s_.id:<30} {alasan}")
            if not args.fase2:
                return 0
            print()

        if pohon.gagal:
            print("=" * 78)
            print("FASE 2 TIDAK DIJALANKAN")
            print("=" * 78)
            print(f"  {pohon.gagal}")
            return 0
        daftar = ambil_definisi(pohon)
        if daftar.gagal:
            print(f"  (daftar definisi: {daftar.gagal})")
        else:
            print(f"  Definisi terbaca: {', '.join(daftar.istilah_saja())}")
        temuan = jalankan_mekanis(pohon, daftar, paragraf)
        for urut, t in enumerate(temuan, start=1):
            t.nomor = urut
    else:
        temuan = jalankan_semua(paragraf, jenis)

    _cetak_temuan(temuan)

    if not temuan:
        print()
        print("Tidak ada temuan. Periksa apakah itu memang benar, atau justru tanda")
        print("bahwa parser gagal mengenali struktur dokumennya — bandingkan dengan")
        print("daftar paragraf di atas.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
