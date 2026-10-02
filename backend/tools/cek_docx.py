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
    import docx  # noqa: F401 — penanda saja; pembacanya di tools/baca_docx.py
except ImportError:
    print("python-docx belum terpasang. Jalankan:  pip install python-docx")
    raise SystemExit(1)

from tools.baca_docx import baca_docx

from app.models.temuan import JenisDokumen, KerangkaTabel, ParagrafInput
from app.rules.format_baku import jalankan_semua
from app.telaah.tahap1_parser.definisi import ambil_definisi
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan.mekanis_konsistensi import jalankan_mekanis


def baca_naskah(
    path: Path, dengan_format: bool = False
) -> tuple[list[dict], list[ParagrafInput], list[KerangkaTabel]]:
    """Entri mentah, paragraf siap kirim, dan kerangka tabel raksasa.

    Paragrafnya menurut urutan `body.paragraphs` di Word. Tiap entri berisi
    medan `ParagrafInput` — teks, penanda, tingkat, letak tabel/baris/sel,
    gambar, rumus, letak_pasti — ditambah `dari_tabel`.

    `penanda` adalah nomor otomatis Word — "Pasal 5", "(2)", "a." — yang TIDAK
    ikut di `paragraph.text` dan karena itu harus dihitung sendiri. Pada naskah
    PMK sungguhan 60% paragrafnya bernomor otomatis, jadi tanpa ini alat
    diagnosa membaca naskah yang berbeda dari yang dibaca add-in.

    Pembacanya di `tools/baca_docx.py`: tiap sel dibaca SEKALI (bug 10), dan
    tabel raksasa jadi kerangka seperti di panel.
    """
    entri, kerangka = baca_docx(path, dengan_format=dengan_format)
    paragraf = [
        ParagrafInput(
            index=e["index"],
            teks=e["teks"],
            penanda=e.get("penanda", ""),
            tingkat=e.get("tingkat", -1),
            tabel=e.get("tabel", -1),
            baris=e.get("baris", -1),
            sel=e.get("sel", -1),
            gambar=e.get("gambar", 0),
            rumus=e.get("rumus", 0),
            letak_pasti=e.get("letak_pasti", True),
            format=e.get("format"),
        )
        for e in entri
    ]
    return entri, paragraf, [KerangkaTabel(**k) for k in kerangka]


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


def _jalankan_lanjut(paragraf, tabel_raksasa, args) -> int:
    """Jalankan seluruh Fase 2 (dan 3) terhadap naskah ini. MEMANGGIL MODEL.

    Ini satu-satunya cara menguji jalur AI tanpa membuka Word. Yang dicetak
    bukan cuma temuannya melainkan juga YANG GUGUR di tahap 5 dan ongkosnya —
    dua angka yang menentukan apakah alat ini layak dipakai, dan dua-duanya
    tidak kelihatan dari panel.
    """
    from app.bersama.llm import KlienAzure, PerapalAzure
    from app.bersama.opensearch import KorpusOpenSearch, PencariOpenSearch
    from app.core.config import settings
    from app.telaah.alur import jalankan_lanjut
    from app.telaah.ekspor.tahap3 import susun_ekspor_tahap3
    from app.telaah.ekspor.tahap4 import susun_ekspor_tahap4
    from app.telaah.ekspor.tahap5 import susun_ekspor_tahap5
    from app.telaah.tahap2_persiapan.bahan import angka

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

    def lapor(tahap: str, selesai: int, total: int) -> None:
        print(f"  Tahap {tahap}: {selesai}/{total}")

    print("=" * 78)
    print("FASE 2 — JALUR AI (memanggil model, berbiaya)")
    print("=" * 78)

    hasil = jalankan_lanjut(
        paragraf,
        klien=klien,
        korpus=korpus,
        perapal=perapal,
        pencari=pencari,
        ambang=args.ambang if args.ambang is not None else settings.FASE2_AMBANG_SKOR,
        lapor=lapor,
        tabel_raksasa=tabel_raksasa,
        anggaran=settings.FASE2_ANGGARAN_TOKEN,
        pasal_per_fokus=settings.FASE2_PASAL_PER_FOKUS,
        berbarengan=settings.FASE2_PANGGILAN_BERBARENGAN,
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
    if hasil.bahan is not None:
        print(f"  Bahan   : ±{angka(hasil.bahan.total_token)} token ({hasil.bahan.cara_hitung})")
    print(f"  Dugaan  : {len(hasil.dugaan)} dari tahap 3")
    print(f"  Ongkos  : {hasil.ongkos.ringkas()}")
    print()

    # Pesan dan hasil dari analisis yang BARU SAJA berjalan, apa adanya.
    if args.tahap3:
        print(susun_ekspor_tahap3(hasil.pesan_tahap3))
    if args.tahap4:
        print(susun_ekspor_tahap4(hasil.pesan_tahap4))
    if args.tahap5:
        print(susun_ekspor_tahap5(hasil))

    _cetak_temuan(hasil.temuan)

    if hasil.jejak_tahap3:
        print()
        print("CATATAN TAHAP 3")
        for c in hasil.jejak_tahap3:
            print(f"  {c}")

    # Yang gugur sama pentingnya dengan yang lolos: inilah bukti tahap 5
    # benar-benar bekerja, bukan cuma ada.
    if hasil.gugur:
        print()
        print("=" * 78)
        print(f"GUGUR ATAU DITURUNKAN : {len(hasil.gugur)}")
        print("=" * 78)
        for g in hasil.gugur:
            print(f"  {g}")
    print()
    return 0


def _jalankan_agen(paragraf, tabel_raksasa, args, path) -> int:
    """Fase 4 — agen penuh. MEMANGGIL MODEL dan BERBIAYA.

    Format paragraf dan halaman dibaca dari .docx (tools/baca_format.py) —
    di add-in Office.js yang membacanya. Ekspor tahap 1–3 Fase 4 dicetak bila
    diminta, persis seperti dari panel.
    """
    import time

    from app.bersama.llm import KlienAzure, PerapalAzure
    from app.bersama.opensearch import KorpusOpenSearch, PencariOpenSearch
    from app.core.config import settings
    from app.models.temuan import FormatHalaman
    from app.telaah.alur import jalankan_agen
    from app.telaah.ekspor.tahap1_bahan import susun_ekspor_tahap1_bahan
    from app.telaah.ekspor.tahap2_jejak_agen import susun_ekspor_tahap2_jejak
    from app.telaah.ekspor.tahap3_verifikasi import susun_ekspor_tahap3_verifikasi
    from app.telaah.tahap2_agen.langkah3_jalankan_agen import Setelan
    from tools.baca_docx import baca_halaman_docx

    klien = KlienAzure()
    if not klien.siap:
        print("Azure OpenAI belum terkonfigurasi. Periksa lewat GET /cek-env.")
        return 1
    korpus = perapal = pencari = None
    if args.fase3:
        k, pr = KorpusOpenSearch(), PerapalAzure()
        if k.siap and pr.siap:
            korpus, perapal = k, pr
        c = PencariOpenSearch()
        pencari = c if c.siap else None
    halaman = [FormatHalaman(**h) for h in baca_halaman_docx(path)]
    kode = [x.strip() for x in args.analisis.split(",") if x.strip()] if args.analisis else None

    def lapor(tahap, selesai, total):
        print(f"  [{time.strftime('%H:%M:%S')}] tahap {tahap}: {selesai}/{total}", flush=True)

    def lapor_putaran(kode_p, keadaan):
        if keadaan.get("keadaan") in ("selesai", "macet", "gagal", "dibatalkan", "menilai"):
            print(
                f"  [{time.strftime('%H:%M:%S')}] {keadaan['judul']}: {keadaan['keadaan']} · "
                f"{keadaan['langkah']} request · {keadaan['calon']} calon",
                flush=True,
            )

    # Jawaban model disimpan di folder ekspor (jawaban.json): jalan ulang atas
    # naskah dan pesan yang sama memakai jawaban itu tanpa membayar lagi —
    # dipakai saat membetulkan gerbang lalu menguji ulang hasil yang sama.
    import json
    import threading

    tersimpan: dict[str, str] = {}
    kunci_berkas = threading.Lock()
    berkas_jawaban = Path(args.simpan_ekspor) / "jawaban.json" if args.simpan_ekspor else None
    if berkas_jawaban is not None and berkas_jawaban.exists():
        tersimpan = json.loads(berkas_jawaban.read_text(encoding="utf-8"))
        print(f"  {len(tersimpan)} jawaban tersimpan dipakai ulang dari {berkas_jawaban}")

    def simpan_jawaban(kunci: str, jawaban: str) -> None:
        if berkas_jawaban is None:
            return
        with kunci_berkas:
            tersimpan[kunci] = jawaban
            berkas_jawaban.parent.mkdir(parents=True, exist_ok=True)
            berkas_jawaban.write_text(json.dumps(tersimpan, ensure_ascii=False), encoding="utf-8")

    print("=" * 78)
    print("FASE 4 — AGEN (memanggil model, berbiaya)")
    print("=" * 78)
    mulai = time.monotonic()
    hasil = jalankan_agen(
        paragraf,
        jenis_panel=args.jenis,
        klien=klien,
        kode_dipilih=kode,
        korpus=korpus,
        perapal=perapal,
        pencari=pencari,
        halaman=halaman,
        tabel_raksasa=tabel_raksasa,
        ambang=args.ambang if args.ambang is not None else settings.FASE2_AMBANG_SKOR,
        tersimpan=tersimpan,
        simpan=simpan_jawaban,
        lapor=lapor,
        lapor_putaran=lapor_putaran,
        setelan=Setelan(settings.FASE4_MACET_ULANG, settings.FASE4_MACET_LANGKAH, settings.FASE4_TUNGGU_429),
        anggaran=settings.FASE2_ANGGARAN_TOKEN,
        per_fokus=settings.FASE2_PASAL_PER_FOKUS,
        token_per_fokus=settings.FASE2_TOKEN_PER_FOKUS,
        berbarengan=settings.FASE2_PANGGILAN_BERBARENGAN,
    )
    print(f"  Selesai dalam {time.monotonic() - mulai:.0f} dtk · ongkos: {hasil.ongkos.ringkas()}, cache {hasil.ongkos.token_cache}")
    if args.simpan_ekspor:
        folder = Path(args.simpan_ekspor)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "ekspor1_bahan.txt").write_text(susun_ekspor_tahap1_bahan(hasil), encoding="utf-8")
        (folder / "ekspor2_jejak.txt").write_text(susun_ekspor_tahap2_jejak(hasil), encoding="utf-8")
        (folder / "ekspor3_gerbang.txt").write_text(susun_ekspor_tahap3_verifikasi(hasil), encoding="utf-8")
        print(f"  Ekspor disimpan di {folder}")
    if args.tahap1:
        print(susun_ekspor_tahap1_bahan(hasil))
    if args.tahap2:
        print(susun_ekspor_tahap2_jejak(hasil))
    print(susun_ekspor_tahap3_verifikasi(hasil))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Periksa rancangan .docx dengan aturan Fase 1")
    ap.add_argument("berkas", help="Path ke rancangan .docx")
    ap.add_argument("--paragraf-saja", action="store_true", help="Hanya tampilkan paragraf, tanpa menjalankan aturan")
    ap.add_argument("--batas", type=int, default=60, help="Jumlah paragraf yang ditampilkan (default 60, 0 = semua)")
    ap.add_argument("--struktur", action="store_true", help="Tampilkan pohon satuan hasil parser Fase 2")
    ap.add_argument("--fase2", action="store_true", help="Jalankan pemeriksaan kode Fase 2 (F2-001..007), bukan Fase 1")
    ap.add_argument("--tahap1", action="store_true", help="ALAT PENGEMBANG: hasil parser — pohon satuan, definisi, lampiran. Gratis")
    ap.add_argument("--tahap2", action="store_true", help="ALAT PENGEMBANG: perkiraan token, lalu bahan persis untuk AI. Gratis")
    ap.add_argument("--lanjut", action="store_true", help="Jalankan SELURUH Fase 2 termasuk jalur AI. MEMANGGIL MODEL dan BERBIAYA.")
    ap.add_argument("--fase3", action="store_true", help="Bersama --lanjut: cari pembanding di korpus peraturan (OpenSearch + embedding).")
    ap.add_argument("--tahap3", action="store_true", help="Bersama --lanjut: cetak pesan tahap 3 (cari dugaan) persis seperti dikirim ke AI.")
    ap.add_argument("--tahap4", action="store_true", help="Bersama --lanjut: cetak pesan tahap 4 berikut hasil alat, persis seperti dibaca AI.")
    ap.add_argument("--tahap5", action="store_true", help="Bersama --lanjut: cetak nasib tiap dugaan — lolos atau gugur, berikut alasannya.")
    ap.add_argument("--ambang", type=float, default=None, help="Ambang skor tahap 5. Bawaan dari core/config.py.")
    ap.add_argument("--jenis", choices=["PMK", "KMK"], default="PMK", help="Jenis dokumen; di add-in ini dipilih penelaah (default PMK)")
    ap.add_argument("--agen", action="store_true", help="FASE 4: jalankan agen penuh. MEMANGGIL MODEL dan BERBIAYA. Bersama --tahap1/--tahap2: cetak ekspor bahan/jejak.")
    ap.add_argument("--analisis", default="", help="Bersama --agen: kode analisis yang dijalankan, dipisah koma (bawaan semua).")
    ap.add_argument("--simpan-ekspor", default="", help="Bersama --agen: folder tempat ekspor tahap 1–3 disimpan.")
    args = ap.parse_args()

    path = Path(args.berkas)
    if not path.exists():
        print(f"Berkas tidak ditemukan: {path}")
        return 1

    entri, paragraf, tabel_raksasa = baca_naskah(path, dengan_format=args.agen)

    if args.agen:
        return _jalankan_agen(paragraf, tabel_raksasa, args, path)
    jml_tabel = sum(1 for e in entri if e["dari_tabel"])

    # --tahap1 dan --tahap2 mencetak ekspornya SAJA — sama persis dengan
    # berkas Ekspor Tahap 1/2 dari panel — jadi kepala ini dilewati.
    if not (args.tahap1 or args.tahap2):
        print("=" * 78)
        print(f"BERKAS : {path.name}")
        print(f"PARAGRAF: {len(entri)} total, {jml_tabel} di antaranya berasal dari dalam tabel")
        if tabel_raksasa:
            print(
                f"TABEL RAKSASA: {len(tabel_raksasa)} tabel tidak dibaca per paragraf — "
                "dikirim kerangkanya saja, seperti di panel"
            )
        print("=" * 78)
        print()

        batas = len(entri) if args.batas == 0 else min(args.batas, len(entri))
        print(f"--- {batas} paragraf pertama (ditampilkan apa adanya, termasuk spasi/tab) ---")
        for i in range(batas):
            tanda = f"[T{entri[i]['tabel']}:{entri[i]['baris']}:{entri[i]['sel']}]" if entri[i]["dari_tabel"] else ""
            pen = entri[i].get("penanda", "")
            awalan = f"{pen!r:<12}" if pen else " " * 12
            print(f"{i:>4} {tanda:<12} {awalan} {entri[i]['teks']!r}")
        if batas < len(entri):
            print(f"     ... {len(entri) - batas} paragraf berikutnya tidak ditampilkan (pakai --batas 0 untuk semua)")
        print()

    if args.paragraf_saja:
        return 0

    jenis = JenisDokumen(args.jenis)

    if args.tahap1:
        from app.telaah.ekspor.tahap1 import susun_ekspor_tahap1

        print(susun_ekspor_tahap1(paragraf, tabel_raksasa))
        return 0

    if args.tahap2:
        from app.core.config import settings
        from app.telaah.ekspor.tahap2 import susun_ekspor_tahap2

        print(
            susun_ekspor_tahap2(
                paragraf,
                tabel_raksasa,
                anggaran=settings.FASE2_ANGGARAN_TOKEN,
                pasal_per_fokus=settings.FASE2_PASAL_PER_FOKUS,
            )
        )
        return 0

    if args.lanjut:
        return _jalankan_lanjut(paragraf, tabel_raksasa, args)

    if args.struktur or args.fase2:
        pohon = bangun_pohon(paragraf)
        if args.struktur:
            from app.telaah.ekspor.tahap1 import teks_di_luar_satuan

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
            lepas = teks_di_luar_satuan(paragraf, pohon)
            print()
            print(
                f"  PARAGRAF BATANG TUBUH DI LUAR TEKS SATUAN: {len(lepas)} "
                "(tetap dikirim mentah ke AI; rinciannya di --tahap1)"
            )
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
