"""TAHAP 3 — GERBANG (Fase 4). SATU-SATUNYA tempat calon jadi Temuan.

Agen bebas memilih langkah, tetapi tidak pernah bebas menandai naskah. Yang
masuk ke sini calon yang sudah DISETUJUI penilai kedua; yang diuji di sini
bukan pendapat siapa pun, melainkan hal yang bisa dibuktikan kode. Seluruh
pemeriksaan gerbang lama (`tahap5_verifikasi.py`) tetap berlaku dan dipakai
ulang fungsinya; yang ditambahkan aturan Fase 4.

GUGUR bila:
  · kutipannya tidak persis ada di letak yang disebut
  · nomor pasal yang disebut tidak ada
  · skornya di bawah ambang
  · yang diklaim "tidak ada" ternyata ada di naskah
  · bukti formatnya tidak cocok dengan bacaan format paragraf itu
  · pembanding atau status peraturannya tidak ada di hasil cari_korpus /
    cek_peraturan yang tercatat
  · yang ditandai cuma rujukan internal yang tujuannya ada (kecuali I-37)
  · menuduh istilah tak berdefinisi padahal tertulis di Pasal 1
  · rumusan dua arah tanpa dua bacaan yang berbeda
  · Periksa ulang: letak dan kutipannya bertindihan dengan temuan lama, apa
    pun kode analisisnya

DITURUNKAN jadi kuning bila:
  · bentuknya melewati baris Respons analisisnya — batas atas, tidak pernah
    dinaikkan
  · usulan tidak muat di tempat yang dicoret, kata tambahannya tidak
    bersumber, atau istilah berdefinisi tidak dieja persis → usulannya jadi
    contoh di Saran
  · dibuang bukan karena tiga alasan yang bisa dibuktikan kode

DILENGKAPI:
  · rujukan dari baris Dasar; Dasar kosong → rujukan agen yang terbukti ada di
    teks skill atau hasil korpus; tidak terbukti → tanpa rujukan
  · isi sisipan cocok dengan korpus → Sumber usulan menyebut peraturannya;
    tidak → "(prediksi AI)"
  · calon kembar digabung ("+n tempat lain")
  · letak tidak pasti → hanya di panel, tidak ditandai
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Optional

from app.models.pekerjaan import CalonAgen, CalonTemuan
from app.models.satuan import JenisSatuan, PohonSatuan
from app.models.temuan import (
    JenisTanda,
    LokasiTemuan,
    ParagrafInput,
    RujukanTemuan,
    Sisipan,
    StatusTemuan,
    Temuan,
)
from app.telaah.tahap1_bahan.langkah3_istilah_pasal1 import DaftarDefinisi
from app.telaah.tahap1_bahan.langkah4_teks_dirujuk import frasa_rujukan_saja
from app.telaah.tahap2_agen.langkah1_pilih_analisis import Analisis, Katalog
from app.telaah.tahap2_agen.langkah3_alat_agen import (
    BahanAlat,
    CatatanPutaran,
    jumlah_kemunculan,
    paragraf_letak,
)
from app.telaah.tahap5_verifikasi import (
    CATATAN_TIDAK_PASTI,
    LETAK_TIDAK_PASTI,
    _KLAIM_TAK_BERDEFINISI,
    _LABEL_DEPAN,
    _letak_pasti,
    _nama_satuan,
    bertindihan,
    cari_di_paragraf,
    definisi_terkait,
    gabungkan_kembar,
    klaim_tidak_ada_keliru,
    periksa_usulan,
    sebutan_sasaran,
    sumber_internal,
    urutan_dokumen,
)

SUMBER_KMK527 = "KMK 527/KMK.01/2022"
PREDIKSI_AI = "(prediksi AI)"
_BOLEH = {
    "otomatis": {"usulan", "dibuang", "catatan"},
    "usulan": {"usulan", "catatan"},
    "dibuang": {"dibuang", "catatan"},
    "catatan": {"catatan"},
}
_HLM = re.compile(r"hlm\s*(\d+(?:\s*[–-]\s*\d+)?)")


_JENIS_LAIN = (
    r"(?:Undang-Undang|UU|Peraturan\s+Pemerintah|PP|Peraturan\s+Presiden|Perpres|"
    r"Peraturan\s+Menteri\s+Keuangan|PMK|Keputusan\s+Menteri\s+Keuangan|KMK)"
)
# "PMK 99 Tahun 2019 Pasal 5" — nama peraturan DULU, pasalnya sesudah. Bentuk
# inilah yang ditulis untuk pembanding korpus.
_PASAL_SESUDAH_NAMA = re.compile(
    rf"\b{_JENIS_LAIN}(?:\s+Nomor)?\s+[\w./-]+(?:\s+Tahun\s+\d{{4}})?\s+Pasal\s+\d+[A-Z]?\b"
)
# "Pasal 5 PMK …" — pasal dulu. "Pasal 9 Peraturan Menteri ini" BUKAN
# peraturan lain: itu naskah ini sendiri, dan nomornya tetap diperiksa.
_PASAL_SEBELUM_NAMA = re.compile(
    r"\bPasal\s+\d+[A-Z]?\s+(?!(?:Peraturan|Keputusan)\s+Menteri\s+ini\b)"
    r"(?:Undang-Undang|Peraturan|Keputusan|UU|PP|PMK|KMK)\b"
)
_PASAL_DISEBUT = re.compile(r"\bPasal\s+(\d+[A-Z]?)\b")


def pasal_karangan_f4(teks: str, pohon: PohonSatuan) -> list[str]:
    """Nomor pasal NASKAH INI yang disebut tetapi tidak ada.

    Pasal peraturan lain tidak diperiksa — dua bentuk penulisannya dibuang
    dulu. Pola gerbang lama hanya mengenali "Pasal 5 PMK …", sehingga
    temuan korpus yang menulis "PMK 99 Tahun 2019 Pasal 5" gugur di naskah
    yang pasalnya kurang dari lima.
    """
    if not teks:
        return []
    bersih = _PASAL_SEBELUM_NAMA.sub(" ", _PASAL_SESUDAH_NAMA.sub(" ", teks))
    hilang: list[str] = []
    for m in _PASAL_DISEBUT.finditer(bersih):
        nomor = m.group(1)
        if not pohon.ada("pasal-" + nomor.lower()) and nomor not in hilang:
            hilang.append(nomor)
    return hilang


def _rapat(t: str) -> str:
    return re.sub(r"\s+", "", t or "").lower()


def _rapi(t: str) -> str:
    return re.sub(r"\s+", " ", t or "").strip()


@dataclass
class Hasil:
    temuan: Optional[Temuan]
    alasan: str = ""
    diturunkan: list[str] = field(default_factory=list)


@dataclass
class BahanGerbang:
    """Yang dibaca gerbang — sama untuk semua calon satu analisis."""

    bahan: BahanAlat
    definisi: DaftarDefinisi
    katalog: Katalog
    catatan: dict[str, CatatanPutaran]
    """judul putaran → catatan alat putaran itu (hasil korpus, status peraturan)."""
    teks_tambahan: list[str] = field(default_factory=list)
    ambang: float = 0.7
    temuan_lama: list[Temuan] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Rujukan
# ---------------------------------------------------------------------------


_BARIS_KAIDAH = re.compile(
    r'^-\s+\*\*(?P<alamat>[^*]+?),\s*hlm\s*(?P<hlm>[0-9]+(?:\s*[–-]\s*[0-9]+)?)\*\*\s*—\s*"(?P<kutipan>.+)"\s*$'
)
_DAFTAR_DAN = re.compile(r"^(?P<kepala>.*\b(?:butir|huruf|angka))\s+(?P<pertama>\S+?)(?P<sisa>(?:\s+dan\s+\S+)+)$")


def kaidah_skill(katalog: Katalog) -> list[tuple[str, str, str]]:
    """(alamat, halaman, kutipan) tiap butir kaidah yang DIKUTIP di teks skill.

    Bentuk barisnya satu: `- **Lampiran II … butir 8, hlm 30** — "…"`. Baris
    lain (bagan, ringkasan) tidak dihitung kutipan — tidak bisa dibuktikan.
    """
    hasil = []
    for s in katalog.skill.values():
        for baris in s.teks.splitlines():
            m = _BARIS_KAIDAH.match(baris.strip())
            if m:
                hasil.append((_rapi(m["alamat"]), m["hlm"].replace(" ", ""), m["kutipan"].strip()))
    return hasil


def _alamat_tunggal(alamat: str) -> list[str]:
    """'Lampiran II … butir 61 dan 64, hlm 45; Lampiran III …' → alamat per butir, tanpa hlm.

    Bentuk yang tidak bisa diurai pasti ("huruf b, c, dan h") dibiarkan
    utuh — tidak akan cocok dengan baris mana pun, jadi tanpa kutipan.
    """
    hasil = []
    for bagian in alamat.split(";"):
        inti = re.split(r",\s*hlm\b", bagian, maxsplit=1)[0].strip()
        inti = re.sub(r"^KMK\s+527(?:/KMK\.01/2022)?\s+", "", inti)
        m = _DAFTAR_DAN.match(inti)
        if m:
            hasil.append(f"{m['kepala']} {m['pertama']}")
            hasil += [f"{m['kepala']} {x}" for x in re.findall(r"\s+dan\s+(\S+)", m["sisa"])]
        elif inti:
            hasil.append(inti)
    return hasil


def _kutipan_skill(alamat: str, katalog: Katalog) -> str:
    """Kutipan butir di teks skill untuk alamat Dasar — alamatnya wajib PERSIS sama.

    'butir 5' tidak boleh mengambil kutipan 'butir 54'. Alamat jamak ("61 dan
    64") diambil kutipan tiap butirnya.
    """
    kaidah = kaidah_skill(katalog)
    kutipan = []
    for satu in _alamat_tunggal(alamat):
        for a, _, k in kaidah:
            if _rapat(a) == _rapat(satu) and k not in kutipan:
                kutipan.append(k)
                break
    return " | ".join(kutipan)


def rujukan_dari_dasar(a: Analisis, katalog: Katalog) -> Optional[RujukanTemuan]:
    """Rujukan dari baris Dasar. None bila Dasar kosong (agen yang mencarikan).

    `butir` memuat alamat lengkap berikut halamannya, persis baris Dasar tanpa
    "KMK 527" dan penanda statusnya — Lampiran → angka → huruf → butir → hlm.
    """
    if a.dasar_status == "prioritas":
        return RujukanTemuan(sumber="prioritas penelaah", butir="", kutipan="", pdf_url="", halaman="", status="prioritas")
    if a.dasar_status in ("visual", "turunan"):
        m = _HLM.search(a.dasar)
        return RujukanTemuan(
            sumber=SUMBER_KMK527,
            butir=a.dasar,
            kutipan=_kutipan_skill(a.dasar, katalog),
            pdf_url="",
            halaman=m.group(1).replace(" ", "") if m else "",
            status=a.dasar_status,
        )
    return None


def bukti_rujukan_agen(c: CalonAgen, g: BahanGerbang) -> Optional[RujukanTemuan]:
    """Rujukan yang dicarikan agen — alamat DAN kutipannya wajib ada di teks skill.

    Keduanya di BARIS KAIDAH YANG SAMA, alamatnya persis sama (bukan
    awalan: "butir 5" bukan "butir 54"), kutipannya ≥ 15 huruf bagian dari
    kutipan baris itu. Alamat dan halaman yang ditulis diambil dari baris
    skill, bukan dari agen. Peraturan lain: alamatnya wajib ada di hasil
    cari_korpus putaran itu. Tidak terbukti → None (tanpa rujukan, tidak
    dikarang).
    """
    if not c.rujukan:
        return None
    alamat = _rapi(str(c.rujukan.get("alamat", "")))
    kutipan = _rapi(str(c.rujukan.get("kutipan", "")))
    if not alamat:
        return None
    satu = _alamat_tunggal(alamat)
    if len(satu) == 1 and len(_rapat(kutipan)) >= 15:
        for a, hlm, k in kaidah_skill(g.katalog):
            if _rapat(a) == _rapat(satu[0]) and _rapat(kutipan) in _rapat(k):
                return RujukanTemuan(
                    sumber=SUMBER_KMK527, butir=f"{a}, hlm {hlm}", kutipan=kutipan, pdf_url="",
                    halaman=hlm, status="agen",
                )
    cat = g.catatan.get(c.putaran)
    if cat is not None:
        for cari in cat.korpus:
            for p in cari["pembanding"]:
                if _rapat(p["sebutan"]) and _rapat(p["sebutan"]) in _rapat(alamat):
                    return RujukanTemuan(
                        sumber=p["sebutan"], butir=(p.get("pasal") or "").replace("-", " "),
                        kutipan=_rapi(p.get("potongan", ""))[:300], pdf_url="", halaman="", status="agen",
                    )
    return None


# ---------------------------------------------------------------------------
# Korpus
# ---------------------------------------------------------------------------


def _pembanding_tercatat(nama: str, cat: Optional[CatatanPutaran]) -> Optional[dict]:
    """Pembanding yang disebut agen, dicocokkan ke hasil cari_korpus yang tercatat."""
    if cat is None or not nama.strip():
        return None
    semua = [p for cari in cat.korpus for p in cari["pembanding"]]
    persis = [p for p in semua if _rapat(p["sebutan"]) == _rapat(nama) or _rapat(f"{p['sebutan']} {p.get('pasal', '')}") == _rapat(nama)]
    if persis:
        return persis[0]
    # Nama yang disalin berikut judul/pasalnya tetap diterima asal sebutan
    # resminya ada di dalamnya, dan cocoknya TUNGGAL — sama seperti alur lama.
    cocok = {p["sebutan"]: p for p in semua if p["sebutan"] and _rapat(p["sebutan"]) in _rapat(nama)}
    return next(iter(cocok.values())) if len(cocok) == 1 else None


def _sebut_pembanding(p: dict) -> str:
    pasal = (p.get("pasal") or "").replace("pasal-", "Pasal ").strip()
    return f"{p['sebutan']}{' ' + pasal if pasal else ''} (masih berlaku)"


def _status_tercatat(c: CalonAgen, cat: Optional[CatatanPutaran]) -> Optional[dict]:
    if cat is None:
        return None
    from app.bersama.opensearch import baca_kutipan

    k = baca_kutipan(c.kutipan) or baca_kutipan(c.status_peraturan)
    for sebutan, isi in cat.peraturan.items():
        if k is not None and isi.get("kutipan") == str(k):
            return isi
        if _rapat(sebutan) and _rapat(sebutan) in _rapat(c.kutipan):
            return isi
    return None


# ---------------------------------------------------------------------------
# Letak
# ---------------------------------------------------------------------------


def _anchor_terlihat(p: ParagrafInput, sembunyi: str, g: BahanGerbang) -> Optional[tuple[ParagrafInput, int, int]]:
    """Kata terlihat untuk menempelkan komentar tanpa warna.

    Teks tersembunyi tidak bisa disorot — tidak tampil di Word — dan paragraf
    kosong bernomor tidak punya huruf. Komentarnya menempel pada kata terlihat
    pertama sesudah teks tersembunyi di paragraf yang sama, atau pada kata
    terakhir paragraf berisi sebelumnya.
    """
    teks = p.teks
    if sembunyi:
        lok = cari_di_paragraf(teks, sembunyi)
        mulai = (lok[0] + lok[1]) if lok else 0
        m = re.search(r"[^\W_][\w/.-]*", teks[mulai:])
        if m:
            return p, mulai + m.start(), len(m.group(0))
    urut = [q for q in g.bahan.paragraf if q.index < p.index]
    for q in reversed(urut):
        t = q.teks.rstrip()
        if not t.strip():
            continue
        m = re.search(r"(\S+)\s*$", t)
        if m:
            return q, m.start(1), len(m.group(1))
    return None


CATATAN_KUTIPAN_GANDA = (
    " (Tidak ditandai di naskah: kutipannya muncul lebih dari sekali di tempat itu, "
    "jadi yang dimaksud tidak bisa dipastikan.)"
)


def _cari_kutipan(c: CalonAgen, par: list[ParagrafInput]) -> Optional[tuple[ParagrafInput, int, int, str, int]]:
    """(paragraf, awal, panjang, kutipan dipakai, jumlah kemunculan). Label di depan dilepas bila perlu.

    Jumlah kemunculan lebih dari satu berarti tempat yang dimaksud TIDAK
    PASTI — yang pertama belum tentu yang salah (PMK 45, 2 Okt 2026: "YANG
    DIPERGUNAKAN" dua kali di baris Menetapkan, yang ditandai yang benar).
    """
    for kutipan in (c.kutipan, _LABEL_DEPAN.sub("", c.kutipan, count=1)):
        if not kutipan.strip():
            continue
        for p in par:
            lok = cari_di_paragraf(p.teks, kutipan)
            if lok is not None:
                return p, lok[0], lok[1], kutipan, jumlah_kemunculan(kutipan, par)
    return None


# ---------------------------------------------------------------------------
# Satu calon
# ---------------------------------------------------------------------------


def verifikasi_satu(c: CalonAgen, g: BahanGerbang) -> Hasil:
    a = g.katalog.cari(c.analisis)
    if a is None:
        return Hasil(None, f"analisis {c.analisis} tidak dikenal")
    pohon: PohonSatuan = g.bahan.pohon
    cat = g.catatan.get(c.putaran)
    turun: list[str] = []

    if c.skor < g.ambang:
        return Hasil(None, f"skor {c.skor:.2f} di bawah ambang {g.ambang:.2f}")
    if hilang := pasal_karangan_f4(c.temuan + " " + c.saran, pohon):
        return Hasil(None, "menyebut Pasal yang tidak ada: " + ", ".join(hilang))

    par = paragraf_letak(c.letak, g.bahan)
    if par is None:
        return Hasil(None, f"letak {c.letak!r} tidak ada di peta letak")

    # --- Bukti format -------------------------------------------------------
    sembunyi = ""
    butir_kosong = False
    if a.format or c.bukti_format:
        if not c.bukti_format:
            return Hasil(None, "analisis format tanpa bukti format")
        cocok = [p for p in par if _rapat(c.bukti_format) in _rapat(g.bahan.anotasi_format.get(p.index, ""))]
        if not cocok:
            return Hasil(
                None,
                f"bukti format {c.bukti_format!r} tidak cocok dengan bacaan format {c.letak}: "
                + repr(" | ".join(g.bahan.anotasi_format.get(p.index, "") for p in par)[:200]),
            )
        par = cocok
        if "tersembunyi" in c.bukti_format.lower():
            sembunyi = c.kutipan
        if "butir bernomor tanpa isi" in c.bukti_format.lower():
            butir_kosong = True

    # --- Letak kutipan ------------------------------------------------------
    tanpa_sorot = False
    ganda = False
    if sembunyi or butir_kosong:
        p0 = par[0]
        if sembunyi and cari_di_paragraf(p0.teks, sembunyi) is None and not any(
            _rapat(sembunyi) in _rapat(t) for t in (p0.format.tersembunyi if p0.format else [])
        ):
            return Hasil(None, f"teks tersembunyi {sembunyi!r} tidak ada di {c.letak}")
        anchor = _anchor_terlihat(p0, sembunyi, g)
        if anchor is None:
            return Hasil(None, "tidak ada kata terlihat untuk menempelkan komentar")
        p, awal, panjang = anchor
        kutipan_dipakai = p.teks[awal : awal + panjang]
        tanpa_sorot = True
    else:
        ketemu = _cari_kutipan(c, par)
        if ketemu is None:
            return Hasil(None, f"kutipan tidak ketemu persis di {c.letak}: {c.kutipan!r}")
        p, awal, panjang, kutipan_dipakai, kemunculan = ketemu
        tanpa_sorot = c.ketiadaan
        # Kutipan yang muncul lebih dari sekali di letaknya: tempat yang
        # dimaksud tidak pasti. Temuannya tetap ada di panel, tetapi TIDAK
        # ditandai — CLAUDE.md butir 6. `catat_temuan` sudah menolaknya; ini
        # jaring kedua.
        ganda = kemunculan > 1

    satuan_id = g.bahan.peta.get(p.index) or (c.letak if pohon.cari(c.letak.lower()) else None)
    lokasi = LokasiTemuan(
        paragraf_index=p.index if (p.letak_pasti and not ganda) else LETAK_TIDAK_PASTI,
        offset_mulai=awal,
        panjang=panjang,
        teks_asli=p.teks[awal : awal + panjang],
    )

    # Adaptor ke bentuk lama — supaya pemeriksaan gerbang lama dipakai apa adanya.
    lama = CalonTemuan(
        aturan_id=c.analisis,
        satuan_id=satuan_id or "",
        alasan=c.temuan,
        teks_asli=kutipan_dipakai,
        saran=c.saran,
        sasaran=c.sasaran,
        usulan_rumusan=c.usulan,
        bacaan=c.bacaan,
        tidak_ada=c.tidak_ada,
        skor=c.skor,
        pembanding=c.pembanding,
    )

    # --- Klaim "tidak ada" ----------------------------------------------------
    # "Tidak dipakai" wajib menyebut istilahnya di `tidak_ada`, dan istilah itu
    # bagian dari teks yang ditandai. Tanpa itu yang dicari cuma kutipannya —
    # kalimat definisi utuh memang tidak pernah muncul dua kali, jadi klaimnya
    # "terbukti" tanpa pernah diperiksa.
    if c.analisis == "F2-003" or (c.bentuk == "dibuang" and c.alasan_buang == "tidak_dipakai"):
        if not any(len(_rapat(x)) >= 2 and _rapat(x) in _rapat(kutipan_dipakai) for x in c.tidak_ada):
            return Hasil(None, "klaim tidak dipakai tanpa istilahnya di tidak_ada (bagian dari kutipan) — tidak terbukti")
        if bukti := _dipakai_di_luar(c, p, g):
            return Hasil(None, bukti)
    elif bukti := klaim_tidak_ada_keliru(lama, g.bahan.paragraf, p.index, g.teks_tambahan):
        return Hasil(None, bukti)
    if c.ketiadaan and not (c.tidak_ada or butir_kosong or sembunyi):
        return Hasil(None, "temuan ketiadaan tanpa klaim tidak_ada yang bisa dibuktikan")

    # --- Pemeriksaan gerbang lama ------------------------------------------
    if c.analisis != "I-37":
        rujukan = frasa_rujukan_saja(kutipan_dipakai, satuan_id or "", pohon)
        if rujukan and all(r.tepat for r in rujukan):
            return Hasil(
                None,
                "yang ditandai cuma rujukan internal, dan tujuannya ada di naskah: "
                + ", ".join(r.id_sasaran for r in rujukan),
            )
    if c.sasaran.strip().lower() == "pasal-1" and _KLAIM_TAK_BERDEFINISI.search(c.temuan):
        pasal_1 = pohon.teks_lengkap("pasal-1")
        istilah = kutipan_dipakai.strip()
        if istilah and re.search(r"(?<!\w)" + re.escape(istilah) + r"(?!\w)", pasal_1, re.IGNORECASE):
            return Hasil(None, f"menuduh {istilah!r} tidak berdefinisi, padahal tertulis di Pasal 1")
    bacaan = [b.strip() for b in c.bacaan if b.strip()]
    if c.analisis == "F2-101":
        if len(bacaan) < 2 or _rapat(bacaan[0]) == _rapat(bacaan[1]):
            return Hasil(None, "rumusan dua arah tanpa dua bacaan yang berbeda — tidak terbukti")

    # --- Korpus ---------------------------------------------------------------
    pembanding = None
    if c.pembanding:
        pembanding = _pembanding_tercatat(c.pembanding, cat)
        if pembanding is None:
            return Hasil(None, f"pembanding {c.pembanding!r} tidak ada di hasil cari_korpus yang tercatat")
    if c.analisis == "F3-001":
        if pembanding is None:
            return Hasil(None, "F3-001 tanpa pembanding dari korpus")
        if "berpotensi bertentangan" not in c.temuan.lower():
            return Hasil(None, "F3-001 wajib berbahasa 'berpotensi bertentangan', bukan 'bertentangan'")
    if c.status_peraturan or c.analisis == "F3-002":
        isi = _status_tercatat(c, cat)
        if isi is None:
            return Hasil(None, "status peraturan tidak ada di hasil cek_peraturan yang tercatat")
        if isi.get("berlaku") is not False:
            return Hasil(None, f"cek_peraturan tidak menyatakan Tidak Berlaku: {isi.get('alasan') or 'Berlaku'}")

    # --- Bentuk dalam batas Respons ------------------------------------------
    bentuk = c.bentuk
    usulan = c.usulan
    saran = c.saran
    if bentuk not in _BOLEH.get(a.respons, {"catatan"}):
        turun.append(f"bentuk {bentuk} melewati Respons {a.respons} — jadi catatan")
        bentuk = "catatan"

    sumber_usulan = ""
    if bentuk == "usulan":
        alasan_turun = ""
        if ganda:
            alasan_turun = "kutipannya muncul lebih dari sekali di letaknya — usulan jadi saran"
        elif lokasi.paragraf_index == LETAK_TIDAK_PASTI:
            alasan_turun = "letaknya sesudah tabel raksasa — usulan jadi saran"
        elif tanpa_sorot:
            alasan_turun = "temuan ketiadaan tidak punya teks yang bisa diganti"
        else:
            sebelum = p.teks[:awal]
            if sebab := periksa_usulan(usulan, kutipan_dipakai, sebelum):
                alasan_turun = sebab
            elif g.definisi.gagal is None and (salah := g.definisi.cari_mirip(usulan)):
                alasan_turun = "istilah berdefinisi salah eja di usulan: " + ", ".join(salah)
            else:
                sumber_usulan = _sumber_usulan(c, kutipan_dipakai, satuan_id or "", pembanding, g)
                if not sumber_usulan:
                    alasan_turun = (
                        "usulan tanpa sumber — kata tambahannya tidak ada di naskah sendiri dan "
                        "tidak ada pembanding dari korpus"
                    )
        if alasan_turun:
            turun.append(alasan_turun)
            bentuk = "catatan"

    if bentuk == "dibuang":
        if sebab := _bukti_buang(c, p, kutipan_dipakai, g):
            turun.append(sebab)
            bentuk = "catatan"
            hapus = f'Hapus "{kutipan_dipakai}".'
            saran = f"{saran} {hapus}".strip() if hapus not in saran else saran

    if bentuk != "usulan" and usulan:
        contoh = f'Contoh rumusan: "{usulan}"'
        saran = f"{saran} {contoh}".strip()

    # --- Sisipan satuan baru --------------------------------------------------
    sisipan = None
    if c.sisipan:
        if a.respons not in ("otomatis", "usulan"):
            turun.append(f"sisipan melewati Respons {a.respons} — isinya jadi contoh di saran")
        else:
            sisipan, sebab = _bukti_sisipan(c, g, cat)
            if sisipan is None:
                turun.append(sebab)
        if sisipan is None:
            isi = str(c.sisipan.get("teks", "")).strip()
            if isi:
                saran = f'{saran} Contoh rumusan {c.sisipan.get("bentuk", "satuan")} baru: "{isi}"'.strip()
        elif bentuk != "catatan":
            # Perbaikannya disisipkan di tempat lain; di tempat temuan, teksnya
            # cuma disorot tanpa komentar — tidak dicoret, tidak diganti.
            if usulan:
                saran = f'{saran} Contoh rumusan: "{usulan}"'.strip()
            bentuk = "catatan"
            sumber_usulan = ""

    # --- Sasaran -------------------------------------------------------------
    sasaran_terbaca = "" if sisipan else sebutan_sasaran(c.sasaran, satuan_id or "", pohon)
    id_tujuan = c.sasaran.strip().lower()
    if sasaran_terbaca and id_tujuan == "pasal-1":
        terkait = definisi_terkait(kutipan_dipakai, g.definisi)
        if terkait:
            sasaran_terbaca += " — " + ", ".join(f"angka {n} ({istilah})" for n, istilah, _ in terkait)
            id_tujuan = terkait[0][2]
    sasaran_paragraf = None
    if sasaran_terbaca:
        tujuan = pohon.cari(id_tujuan)
        if tujuan is not None and tujuan.bisa_ditandai and _letak_pasti(g.bahan.paragraf, tujuan.paragraf_mulai):
            sasaran_paragraf = tujuan.paragraf_mulai

    # --- Rujukan -------------------------------------------------------------
    rujukan = rujukan_dari_dasar(a, g.katalog)
    if rujukan is None:
        rujukan = bukti_rujukan_agen(c, g) or RujukanTemuan(
            sumber="", butir="", kutipan="", pdf_url="", halaman="", status="tanpa"
        )

    catatan = c.temuan.strip()
    if len(bacaan) >= 2:
        catatan = f"{catatan} Bisa dibaca: (1) {bacaan[0].rstrip('.')}; atau (2) {bacaan[1].rstrip('.')}."
    if ganda:
        catatan += CATATAN_KUTIPAN_GANDA
    elif lokasi.paragraf_index == LETAK_TIDAK_PASTI:
        catatan += CATATAN_TIDAK_PASTI
    if a.komentar == "ringkas":
        saran = ""

    jenis = (
        JenisTanda.PENGGANTIAN if bentuk == "usulan"
        else JenisTanda.PENGHAPUSAN if bentuk == "dibuang"
        else JenisTanda.CATATAN
    )
    temuan = Temuan(
        id="f-" + uuid.uuid4().hex[:8],
        aturan_id=c.analisis,
        fase=1 if c.analisis.startswith("F1") else 3 if c.analisis.startswith("F3") else 2,
        jenis_tanda=jenis,
        satuan_id=satuan_id,
        skor=c.skor,
        lokasi=lokasi,
        catatan=catatan,
        saran=_rapi(saran),
        sumber_usulan=sumber_usulan if bentuk == "usulan" else (sisipan.sumber if sisipan else ""),
        sasaran=sasaran_terbaca,
        sasaran_paragraf=sasaran_paragraf,
        usulan_rumusan=usulan if bentuk == "usulan" else None,
        tanpa_sorot=tanpa_sorot,
        rujukan=rujukan,
        pembanding=_sebut_pembanding(pembanding) if pembanding else "",
        sisipan=sisipan,
        status=StatusTemuan.BELUM_DITINJAU,
    )
    return Hasil(temuan, diturunkan=turun)


def _dipakai_di_luar(c: CalonAgen, p: ParagrafInput, g: BahanGerbang) -> str:
    """dibuang/tidak_dipakai: teks itu dicari di luar pasal tempatnya. Ketemu → klaimnya keliru."""
    pohon = g.bahan.pohon
    sid = g.bahan.peta.get(p.index, "")
    m = re.match(r"(pasal-[0-9a-z]+)", sid)
    induk = pohon.cari(m.group(1)) if m else None
    lewati = range(induk.paragraf_mulai, induk.paragraf_akhir) if induk else range(p.index, p.index + 1)
    for x in [c.kutipan] + c.tidak_ada:
        kunci = _rapat(x)
        if len(kunci) < 2:
            continue
        for q in g.bahan.paragraf:
            if q.index in lewati:
                continue
            if kunci in _rapat(q.utuh):
                return f"mengklaim {x!r} tidak dipakai, padahal ada di paragraf {q.index}"
        for t in g.teks_tambahan:
            if kunci in _rapat(t):
                return f"mengklaim {x!r} tidak dipakai, padahal ada di contoh tabel raksasa"
    return ""


def _bukti_buang(c: CalonAgen, p: ParagrafInput, kutipan: str, g: BahanGerbang) -> str:
    """Alasan dibuang yang TIDAK terbukti; kosong bila terbukti."""
    if c.alasan_buang == "tidak_dipakai":
        return ""  # sudah dibuktikan _dipakai_di_luar
    if c.alasan_buang == "mengulang":
        par = paragraf_letak(c.bukti_letak, g.bahan) if c.bukti_letak else None
        if not par:
            return "dibuang/mengulang tanpa letak kembaran yang ada — jadi catatan"
        if not any(q.index != p.index and cari_di_paragraf(q.teks, kutipan) for q in par):
            return f"dibuang/mengulang: teks itu tidak ada di {c.bukti_letak} — jadi catatan"
        return ""
    if c.alasan_buang == "frasa_dilarang":
        r = bukti_rujukan_agen(c, g)
        if r is None or _rapat(kutipan) not in _rapat(r.kutipan):
            return "dibuang/frasa_dilarang: frasanya tidak terbukti dilarang kutipan kaidah — jadi catatan"
        return ""
    return "dibuang tanpa alasan yang bisa dibuktikan kode — jadi catatan"


def _sumber_usulan(c: CalonAgen, kutipan: str, satuan_id: str, pembanding: Optional[dict], g: BahanGerbang) -> str:
    if pembanding is not None:
        return _sebut_pembanding(pembanding)
    dalam = sumber_internal(c.usulan, kutipan, satuan_id, g.bahan.pohon, g.definisi)
    if dalam:
        return dalam
    if c.analisis == "S-64":
        # Kata yang dibetulkan wajib terbukti dieja begitu di tempat lain naskah ini.
        baru = [k.strip(".,;:()\"'") for k in c.usulan.split() if k.strip(".,;:()\"'")]
        lama = {k.lower().strip(".,;:()\"'") for k in kutipan.split()}
        tambahan = [k for k in baru if k.lower() not in lama]
        if tambahan and all(
            any(re.search(r"\b" + re.escape(k) + r"\b", q.teks) for q in g.bahan.paragraf)
            for k in tambahan
        ):
            return "ejaan yang sama tertulis di bagian lain naskah ini"
    if c.analisis == "I-37":
        r = frasa_rujukan_saja(c.usulan, satuan_id, g.bahan.pohon)
        if r and all(x.tepat for x in r):
            return "ketentuan yang dirujuk ada di naskah: " + ", ".join(_nama_satuan(x.id_sasaran) for x in r)
    return ""


_BENTUK_ANAK = {
    "angka": JenisSatuan.ANGKA,
    "huruf": JenisSatuan.HURUF,
    "ayat": JenisSatuan.AYAT,
}


def _bukti_sisipan(c: CalonAgen, g: BahanGerbang, cat: Optional[CatatanPutaran]) -> tuple[Optional[Sisipan], str]:
    s = c.sisipan or {}
    pohon = g.bahan.pohon
    sasaran = str(s.get("sasaran", "")).strip().lower()
    bentuk = str(s.get("bentuk", "")).strip().lower()
    teks = _rapi(str(s.get("teks", "")))
    tujuan = pohon.cari(sasaran)
    if tujuan is None or not tujuan.bisa_ditandai:
        return None, f"tempat sisipan {sasaran!r} tidak ada di peta letak"
    if bentuk not in _BENTUK_ANAK:
        return None, f"sisipan {bentuk or '?'} belum didukung — hanya angka, huruf, atau ayat; isinya jadi contoh"
    if not teks:
        return None, "sisipan tanpa isi"
    if not _letak_pasti(g.bahan.paragraf, tujuan.paragraf_akhir - 1):
        return None, "tempat sisipan sesudah tabel raksasa — letaknya di Word tidak pasti"
    anak = [x for x in pohon.anak_dari(tujuan.id) if x.jenis == _BENTUK_ANAK[bentuk]]
    terakhir = max(
        (q.index for q in g.bahan.paragraf if tujuan.paragraf_mulai <= q.index < tujuan.paragraf_akhir and q.teks.strip()),
        default=tujuan.paragraf_akhir - 1,
    )
    penanda = ""
    if anak:
        nomor = anak[-1].nomor.strip("()")
        if bentuk == "angka" and nomor.isdigit():
            penanda = f"{int(nomor) + 1}."
        elif bentuk == "ayat" and nomor.isdigit():
            penanda = f"({int(nomor) + 1})"
        elif bentuk == "huruf" and len(nomor) == 1 and nomor.isalpha() and nomor != "z":
            penanda = f"{chr(ord(nomor) + 1)}."
    sumber = PREDIKSI_AI
    if cat is not None:
        for cari in cat.korpus:
            for p in cari["pembanding"]:
                if len(_rapat(teks)) >= 20 and _rapat(teks) in _rapat(p.get("potongan", "")):
                    sumber = _sebut_pembanding(p)
                    break
            if sumber != PREDIKSI_AI:
                break
    return (
        Sisipan(
            sasaran=tujuan.id,
            sesudah_paragraf=terakhir,
            bentuk=bentuk,
            penanda=penanda,
            teks=teks,
            sumber=sumber,
            letak_ideal="",
            format_dari=anak[-1].paragraf_mulai if anak else -1,
        ),
        "",
    )


def _penanda_ke(penanda: str, bentuk: str, n: int) -> str:
    """Penanda ke-n sesudah `penanda` dalam bentuk yang sama: "3." → "5." untuk n=2."""
    isi = penanda.strip().strip("().")
    if bentuk in ("angka", "ayat") and isi.isdigit():
        baru = int(isi) + n
        return f"({baru})" if bentuk == "ayat" else f"{baru}."
    if bentuk == "huruf" and len(isi) == 1 and isi.isalpha() and ord(isi) + n <= ord("z"):
        return f"{chr(ord(isi) + n)}."
    return ""


def rapikan_sisipan(lolos: list[Temuan], gugur: list[str]) -> None:
    """Sisipan kembar dan penanda kembar di satu tempat — `lolos` sudah urut dokumen.

    Dua temuan yang mengusulkan satuan baru yang SAMA di tempat yang sama
    disisipkan sekali saja. Dua satuan baru BERBEDA di tempat yang sama tidak
    boleh bernomor sama: tiap penanda dihitung dari pohon yang sama, jadi
    keduanya mendapat "18." — yang kedua dinaikkan jadi "19.", menurut urutan
    temuannya di naskah.
    """
    sudah: set[tuple[str, str]] = set()
    per_tempat: dict[tuple[str, str], list[Temuan]] = {}
    for t in lolos:
        s = t.sisipan
        if s is None:
            continue
        kunci = (s.sasaran, _rapat(s.teks))
        if kunci in sudah:
            t.sisipan = None
            t.sumber_usulan = ""
            t.saran = _rapi(f"{t.saran} Satuan baru yang sama sudah diusulkan untuk temuan lain di {_nama_satuan(s.sasaran)}.")
            gugur.append(f"{t.aturan_id} {t.satuan_id}: sisipan kembar dengan temuan lain — disisipkan sekali saja")
            continue
        sudah.add(kunci)
        per_tempat.setdefault((s.sasaran, s.bentuk), []).append(t)
    for (_, bentuk), daftar in per_tempat.items():
        awal = daftar[0].sisipan.penanda if daftar[0].sisipan else ""
        for n, t in enumerate(daftar[1:], start=1):
            if t.sisipan is not None:
                t.sisipan.penanda = _penanda_ke(awal, bentuk, n) if awal else ""


# ---------------------------------------------------------------------------
# Seluruh calon
# ---------------------------------------------------------------------------


def _bertindih_lama(t: Temuan, lama: list[Temuan]) -> Optional[Temuan]:
    """Periksa ulang: letak dan kutipannya bertindihan dengan temuan lama, apa pun kodenya."""
    if (x := bertindihan(t.lokasi, lama)) is not None:
        return x
    kini = _rapat(t.lokasi.teks_asli)
    for x in lama:
        if not kini or not x.satuan_id or x.satuan_id != t.satuan_id:
            continue
        dulu = _rapat(x.lokasi.teks_asli)
        if dulu and (dulu in kini or kini in dulu):
            return x
    return None


def verifikasi(calon: list[CalonAgen], g: BahanGerbang) -> tuple[list[Temuan], list[str]]:
    """Calon yang DISETUJUI penilai kedua → temuan; sisanya alasan gugur/turun."""
    lolos: list[Temuan] = []
    gugur: list[str] = []
    sudah: list[Temuan] = []
    for c in calon:
        nama = f"{c.putaran} {c.nomor} {c.analisis} [{c.letak}]"
        h = verifikasi_satu(c, g)
        if h.temuan is None:
            gugur.append(f"{nama}: GUGUR — {h.alasan}")
            continue
        if (x := _bertindih_lama(h.temuan, g.temuan_lama)) is not None:
            gugur.append(f"{nama}: GUGUR — bertindihan dengan temuan lama T{x.nomor} ({x.aturan_id})")
            continue
        if (x := bertindihan(h.temuan.lokasi, sudah)) is not None:
            gugur.append(f"{nama}: GUGUR — bertindihan dengan temuan {x.aturan_id} pada {x.lokasi.teks_asli!r}")
            continue
        for alasan in h.diturunkan:
            gugur.append(f"{nama}: DITURUNKAN — {alasan}")
        lolos.append(h.temuan)
        sudah.append(h.temuan)
    lolos.sort(key=urutan_dokumen)
    hasil = gabungkan_kembar(lolos, gugur)
    rapikan_sisipan(hasil, gugur)
    return hasil, gugur
