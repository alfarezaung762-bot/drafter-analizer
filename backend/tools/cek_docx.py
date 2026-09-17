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

from app.models.temuan import JenisDokumen, ParagrafInput
from app.rules.format_baku import jalankan_semua


def baca_paragraf(path: Path) -> list[dict]:
    """Baca seluruh paragraf dokumen menurut urutan asli, termasuk isi tabel.

    Tiap entri: {'teks': str, 'dari_tabel': bool}
    """
    doc = Document(str(path))
    hasil: list[dict] = []

    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            hasil.append({"teks": Paragraph(child, doc).text, "dari_tabel": False})
        elif child.tag == qn("w:tbl"):
            tabel = Table(child, doc)
            for baris in tabel.rows:
                for sel in baris.cells:
                    for p in sel.paragraphs:
                        hasil.append({"teks": p.text, "dari_tabel": True})

    return hasil


def main() -> int:
    ap = argparse.ArgumentParser(description="Periksa rancangan .docx dengan aturan Fase 1")
    ap.add_argument("berkas", help="Path ke rancangan .docx")
    ap.add_argument("--paragraf-saja", action="store_true", help="Hanya tampilkan paragraf, tanpa menjalankan aturan")
    ap.add_argument("--batas", type=int, default=60, help="Jumlah paragraf yang ditampilkan (default 60, 0 = semua)")
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
        print(f"{i:>4} {tanda} {entri[i]['teks']!r}")
    if batas < len(entri):
        print(f"     ... {len(entri) - batas} paragraf berikutnya tidak ditampilkan (pakai --batas 0 untuk semua)")
    print()

    if args.paragraf_saja:
        return 0

    paragraf = [ParagrafInput(index=i, teks=e["teks"]) for i, e in enumerate(entri)]
    jenis = JenisDokumen(args.jenis)
    temuan = jalankan_semua(paragraf, jenis)

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
        print(f"  Catatan : {t.catatan}")
        if t.usulan_rumusan:
            print(f"  Usulan  : {t.usulan_rumusan}")
        butir = t.rujukan.butir
        if butir == "...":
            print("  Rujukan : BELUM DIVERIFIKASI — butir dan kutipannya masih placeholder")
        else:
            print(f"  Rujukan : {t.rujukan.sumber} butir {butir}")
    if not temuan:
        print()
        print("Tidak ada temuan. Periksa apakah itu memang benar, atau justru tanda")
        print("bahwa parser gagal mengenali struktur dokumennya — bandingkan dengan")
        print("daftar paragraf di atas.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
