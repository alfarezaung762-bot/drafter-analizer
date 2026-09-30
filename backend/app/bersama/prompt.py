"""Seluruh instruksi ke model, di satu tempat.

Mengikuti pola `rujukan_kmk527.py` di Fase 1: apa pun yang menentukan hasil
harus bisa dibaca dan diperiksa manusia di satu berkas, bukan tersebar jadi
f-string di tujuh tempat.

Mau mengubah perilaku model? Yang disentuh `PERAN` — satu baris.
"""

from __future__ import annotations

from string import Template

PERAN = """Kamu penelaah di Biro Hukum Kementerian Keuangan yang memeriksa
rancangan Peraturan Menteri Keuangan terhadap kaidah penyusunan peraturan.

Tugasmu MENEMUKAN ketentuan yang tidak jelas atau saling bertabrakan — bukan
memperbaiki naskahnya, bukan menilai kebijakannya."""


# Ikut di SETIAP panggilan. Baris-baris ini yang menjaga keluaran model tetap
# bisa diverifikasi kode di tahap 5.
ATURAN_TETAP = """Aturan yang berlaku untuk semua jawabanmu:
- Kutip teks naskah PERSIS, huruf demi huruf. Jangan diparafrase, jangan
  dirapikan, jangan disingkat. Kutipan yang meleset satu kata membuat temuanmu
  tidak bisa dipakai.
- Jangan menyebut nomor pasal atau nomor peraturan yang tidak ada di bahan
  yang diberikan kepadamu.
- Kalau tidak yakin, katakan tidak yakin. Menebak lebih buruk daripada diam.
- Kalau tidak ada yang bermasalah, katakan tidak ada. Jangan mencari-cari.
- Jawab HANYA dengan JSON yang diminta, tanpa penjelasan di luar JSON."""


# ---------------------------------------------------------------------------
# Jenis dugaan — dipakai tahap 3 (mencari) dan tahap 4 (memastikan)
# ---------------------------------------------------------------------------

# Kode jenis → (aturan, keterangan). Keterangan inilah yang dibaca model, jadi
# ia juga yang menentukan apa yang BUKAN temuan.
JENIS: dict[str, tuple[str, str]] = {
    "makna_ganda": (
        "F2-101",
        "rumusan yang bisa dibaca dua arah — ada DUA tafsiran yang sama-sama masuk "
        "akal dan berbeda akibat hukumnya. Termasuk definisi Pasal 1 yang "
        "menimbulkan pengertian ganda (KMK 527 butir 66). \"Terlalu umum\" atau "
        "\"kurang rinci\" BUKAN dua tafsiran.",
    ),
    "pemikul": (
        "F2-102",
        "kewajiban atau larangan yang tidak jelas siapa yang memikulnya — "
        "subjeknya tidak tertulis dan tidak bisa ditarik dari kalimat induk atau "
        "ayat yang merangkainya.",
    ),
    "operasional": (
        "F2-103",
        "kata operasional — wajib, harus, dapat, dilarang — yang bertabrakan di "
        "dalam SATU ketentuan, sehingga tidak jelas perbuatannya diwajibkan atau "
        "dibolehkan. Kata operasional yang berbeda di pasal yang berbeda itu lazim.",
    ),
    "tabrakan": (
        "F2-104",
        "dua ketentuan yang tidak bisa berlaku bersamaan. Sebut KEDUA satuannya. "
        "Pengecualian yang sah — \"kecuali sebagaimana dimaksud dalam Pasal 12\" — "
        "bukan tabrakan.",
    ),
    "cakupan": (
        "F2-105",
        "tujuan yang dinyatakan di Menimbang tetapi tidak ada satu pun "
        "ketentuannya di batang tubuh. satuan_id-nya butir Menimbang itu "
        "(mis. menimbang-b).",
    ),
    "lampiran": (
        "F2-106",
        "lampiran yang tidak sesuai KMK 527 butir 120–121 — lihat parameternya.",
    ),
}


def daftar_jenis(kode: list[str]) -> str:
    """Baris "- nama (aturan): keterangan" untuk jenis yang diminta."""
    return "\n".join(f"- {k} ({JENIS[k][0]}): {JENIS[k][1]}" for k in kode)


# ---------------------------------------------------------------------------
# TAHAP 3 — mencari dugaan, fokus menurut jenis pemeriksaan
# ---------------------------------------------------------------------------

TAHAP3_PER_PASAL = """TUGAS: CARI DUGAAN PADA PASAL FOKUS.

Naskah utuh ada di atas. Periksa HANYA pasal fokus di bawah — tetapi baca tiap
pasal fokus dengan seluruh naskah sebagai konteksnya: definisi di Pasal 1,
pasal yang dirujuknya, bab tempatnya bernaung, dan lampirannya.

Yang dicari:
$jenis

Yang kamu hasilkan DUGAAN, bukan temuan. Tiap dugaan akan diuji ulang pada
teks utuhnya sebelum menyentuh naskah — tetapi jangan mencari-cari. Temuan
pemeriksaan format yang sudah ada tidak perlu kamu ulang.

Pasal fokus: $fokus

WAJIB menjawab SETIAP pasal fokus. Pasal tanpa masalah tetap ditulis dengan
daftar dugaan kosong — pasal yang tidak kamu tulis akan ditanyakan ulang.

Jawab dengan JSON:
{
  "hasil": [
    {
      "pasal": "<id pasal fokus, salin persis, mis. pasal-5>",
      "dugaan": [
        {
          "satuan_id": "<id satuan TERDALAM tempat masalahnya — pasal ini atau
                         ayat/huruf/angka di dalamnya, salin persis dari naskah>",
          "jenis": $kode,
          "alasan": "<satu kalimat: apa yang janggal>",
          "eksternal": true/false
        }
      ]
    }
  ]
}

`eksternal` bernilai true HANYA kalau pembuktiannya menuntut peraturan LAIN di
luar naskah ini. Kalau cukup dibuktikan dari naskah ini saja, false."""


TAHAP3_LINTAS = """TUGAS: CARI DUGAAN LINTAS NASKAH.

Naskah utuh ada di atas. Yang dicari hanya kejanggalan yang baru terlihat kalau
naskah dipandang sebagai satu kesatuan:
$jenis

Yang kamu hasilkan DUGAAN — tiap dugaan diuji ulang pada teks utuhnya sebelum
menyentuh naskah. Jangan mencari-cari.

$keberatan

Jawab dengan JSON:
{
  "dugaan": [
    {
      "satuan_id": "<id satuan utama, salin persis dari naskah>",
      "satuan_lain": "<id satuan kedua kalau tabrakan; kalau bukan, string kosong>",
      "jenis": $kode,
      "alasan": "<satu kalimat: apa yang janggal>",
      "eksternal": true/false
    }
  ],
  "keberatan": [
    {
      "nomor": <nomor temuan format yang kamu keberatani, angka di dalam (T…)>,
      "alasan": "<satu kalimat: kenapa temuan itu menurutmu keliru>"
    }
  ]
}

`eksternal` bernilai true HANYA kalau pembuktiannya menuntut peraturan LAIN di
luar naskah ini."""

TAHAP3_KEBERATAN_ADA = """Temuan pemeriksaan format yang sudah ada tercantum di bagian akhir naskah.
Kalau menurutmu salah satunya KELIRU karena konteks naskah yang lebih luas,
tulis keberatanmu di `keberatan`. Keberatanmu ditempelkan pada temuan itu
sebagai catatan; temuannya tetap ada, dan penelaah yang memutuskan.
`keberatan` boleh kosong, dan seringnya memang kosong — isi hanya kalau
alasannya bisa ditunjuk dari naskah, bukan sekadar merasa janggal."""

TAHAP3_KEBERATAN_TIDAK = "`keberatan` selalu kosong ([]) — tidak ada temuan format yang dilampirkan."

TAHAP3_TANPA_JENIS = (
    "- (tidak ada jenis dugaan yang diminta — `dugaan` selalu kosong, [])"
)


# Parameter F2-106, dibaca dari citra halaman 57 PDF KMK 527 (29 Sep 2026).
# Dipakai tahap 3 (mencari) dan tahap 4 (memastikan) — satu sumber.
PARAMETER_LAMPIRAN = """Dugaan hanya boleh lahir dari pelanggaran salah satu parameter ini:
1. (butir 120) Lampiran wajib dinyatakan di batang tubuh, berikut pernyataan
   bahwa lampiran itu merupakan bagian yang tidak terpisahkan dari Peraturan
   Menteri ini. Periksa: tiap lampiran yang ada disebut pasal, dan kalimat
   penunjuknya memuat pernyataan itu.
2. Lampiran yang disebut pasal wajib ada — misalnya pasal menyebut
   "Lampiran II" padahal lampirannya cuma satu. Sebaliknya juga: lampiran
   yang ada tetapi tidak pernah disebut pasal mana pun.
3. Salah ketik kata "Lampiran" di pasal atau di kepala lampiran.
4. (butir 121 huruf b dan c) Kepala lampiran: kata LAMPIRAN ditulis kapital,
   berangka Romawi I, II, dan seterusnya bila lampirannya lebih dari satu; di
   bawahnya judul PMK — nomor, tahun, dan judulnya wajib sama dengan halaman
   pertama.
5. (butir 121 huruf h) Pada akhir tiap lampiran dicantumkan nama dan tanda
   tangan pejabat yang menetapkan.
6. Bilangan di lampiran yang ditulis angka dan huruf — "30 (tiga puluh)" —
   wajib cocok angka dan hurufnya.

Yang TIDAK diperiksa: tata letak (kanan margin, tengah margin, nomor halaman —
tidak terlihat di teks), isi dan kebijakan lampiran, dan jumlah lampiran
(butir 121 huruf i hanya anjuran)."""


TAHAP3_LAMPIRAN = """TUGAS: PERIKSA LAMPIRAN TERHADAP KMK 527/KMK.01/2022 LAMPIRAN II BUTIR 120–121.

Naskah utuh ada di atas, dan fakta lampiran yang dikumpulkan kode ada di bawah.
Fakta itu BUKAN kesimpulan — pastikan sendiri pada naskahnya.

""" + PARAMETER_LAMPIRAN + """

satuan_id: id pasal/ayat tempat kalimat penunjuknya bermasalah, atau "lampiran"
kalau masalahnya di dalam lampiran.

Jawab dengan JSON:
{
  "dugaan": [
    {
      "satuan_id": "<id satuan, salin persis dari naskah, atau \\"lampiran\\">",
      "alasan": "<satu kalimat, sebut nomor parameter yang dilanggar>"
    }
  ]
}
Kalau tidak ada yang bermasalah: {"dugaan": []}

$fakta"""


# ---------------------------------------------------------------------------
# TAHAP 4 — memastikan, dengan naskah utuh dan alat
# ---------------------------------------------------------------------------

_TAHAP4_ALAT = """ALAT. Sebelum menjawab kamu boleh memakai alat:
- cari_teks — mencari di SELURUH naskah, termasuk lampiran dan isi tabel, tidak
  peka huruf besar-kecil dan jarak spasi. WAJIB dipakai sebelum kamu menyatakan
  sesuatu TIDAK ADA di naskah.
- buka_tabel dan jumlah_kolom — membuka isi tabel lampiran, termasuk yang hanya
  dikirim kerangkanya, dan menjumlah satu kolomnya. Jangan menghitung sendiri."""

_TAHAP4_TIDAK_ADA = """  "tidak_ada": ["<teks yang kamu klaim TIDAK ADA di naskah — pasal, ayat,
                lampiran, atau kata yang kamu cari dan tidak ketemu. Salin
                persis. Kode akan mencarinya di seluruh naskah; kalau ternyata
                ada, dugaanmu gugur. Kosongkan ([]) kalau alasanmu tidak
                mengklaim ketiadaan apa pun>"],"""

TAHAP4_MEMASTIKAN = """TUGAS: MEMASTIKAN SATU DUGAAN.

Naskah utuh ada di atas. Satuan yang diuji, batang kalimat induknya, dan isi
yang dirujuknya diulang di bawah supaya jelas letaknya.

Tugasmu MENGUJI dugaan itu, bukan mencari yang lain. Dugaan yang tidak
terbukti dari naskah harus kamu gugurkan; itu hasil yang baik, bukan kegagalan.

""" + _TAHAP4_ALAT + """

Kalau satuan itu merujuk bagian lain ("sebagaimana dimaksud dalam Pasal …"),
isi bagian yang dirujuk dilampirkan di blok SATUAN YANG DIRUJUK — dicari kode
dari naskah, bukan tebakan. Rujukan yang tujuannya tercantum di sana ADA di
naskah; jangan menuduhnya menunjuk sesuatu yang tidak ada.

Tetapi kalau dugaannya TERBUKTI dan cacatnya ada persis di teks yang kamu
kutip, kamu WAJIB menuliskan penggantinya. Menyatakan sesuatu salah lalu diam
soal betulnya cuma memindahkan seluruh pekerjaan kembali ke penelaah — dan
penelaah sudah tahu naskahnya bermasalah, itu sebabnya ia memakai alat ini.

Jawab dengan JSON:
{
  "terbukti": true/false,
  "alasan": "<kalau terbukti: satu kalimat yang menjelaskan apa yang salah,
              ditujukan kepada penelaah. Kalau tidak terbukti: kenapa gugur>",
  "teks_asli": "<kalau terbukti: potongan teks PERSIS dari satuan itu yang
                 menjadi letak masalahnya. Sependek mungkin, tetapi utuh
                 sebagai frasa, dan WAJIB berada dalam SATU ayat — kutipan
                 yang merentang beberapa ayat tidak akan ketemu di naskah dan
                 temuanmu gugur. Salin huruf demi huruf. Label penomoran
                 seperti (1), a., atau 1. cuma penunjuk susunan, bukan
                 bagian teks — jangan ikut disalin>",
  "saran": "<satu kalimat saran perbaikan untuk penelaah. Boleh menawarkan
             dua jalan kalau memang ada dua. Kalau kamu tidak tahu apa yang
             sebaiknya dilakukan, KOSONGKAN — saran yang cuma mengulang
             masalahnya tidak menolong siapa pun>",
  "sasaran": "<DI MANA perbaikannya dikerjakan. WAJIB salah satu dari:
               'satuan ini' — perbaikannya persis di teks yang kamu kutip
               'pasal-1'    — perlu menambah/mengubah definisi di Ketentuan Umum
               'menimbang' | 'mengingat' | 'menetapkan' | 'judul'
               '<id satuan>' — id satuan LAIN yang memang ada di naskah ini

              SEBUT SESPESIFIK MUNGKIN. Kalau perbaikannya ada di satu ayat
              atau satu huruf tertentu, sebut ayat/huruf itu — bukan pasalnya
              saja. 'pasal-4-ayat-2-huruf-b' jauh lebih menolong daripada
              'pasal-4', karena penelaah tidak perlu membaca ulang seluruh
              pasal untuk menebak yang mana. Pakai id pasal yang polos HANYA
              kalau perbaikannya memang menyangkut seluruh pasal itu.

              Jangan mengarang id. Kalau tidak yakin, tulis 'satuan ini'>",
  "usulan_rumusan": "<PENGGANTI PERSIS UNTUK teks_asli SAJA — bukan untuk
                      kalimatnya, bukan untuk ayatnya. Bayangkan teks_asli
                      dihapus dan tulisan ini ditaruh di tempatnya: kalimatnya
                      harus jadi utuh dan benar, tanpa ada kata yang terulang.
                      JANGAN mengulang kata-kata yang berada SEBELUM teks_asli.

                      WAJIB TERISI kalau 'sasaran' bernilai 'satuan ini'.
                      Susun penggantinya dari kata yang SUDAH ADA di naskah:
                      subjek yang tertulis di ayat lain pasal ini, atau istilah
                      yang sudah berdefinisi di Pasal 1. Jangan membawa masuk
                      istilah baru dari ingatanmu — kode memeriksanya kata demi
                      kata, dan satu kata asing menggugurkan usulanmu.

                      KOSONGKAN hanya dalam dua keadaan:
                        - 'sasaran' menunjuk tempat LAIN (mis. 'pasal-1'),
                          karena perbaikannya memang tidak dikerjakan di sini;
                        - perbaikannya MEMBUANG teks itu, bukan menggantinya.

                      Di luar dua keadaan itu, mengosongkannya adalah kegagalan
                      menjawab — bukan kehati-hatian>",
""" + _TAHAP4_TIDAK_ADA + """
  "bacaan": ["<tafsiran pertama>", "<tafsiran kedua>"]
            — WAJIB untuk dugaan jenis makna_ganda: dua cara membaca
            rumusan itu yang SAMA-SAMA masuk akal dan BERBEDA akibat
            hukumnya. Tulis keduanya sebagai kalimat utuh. Kalau kamu tidak
            bisa menuliskan dua tafsiran yang berbeda, dugaannya TIDAK
            terbukti — "terlalu umum", "kurang rinci", atau "sebaiknya
            dirinci" bukan dua tafsiran. Untuk jenis lain, kosongkan ([]),
  "skor": <0.0 sampai 1.0, seberapa yakin kamu>
}"""


TAHAP4_TABRAKAN = """TUGAS: MEMASTIKAN DUGAAN TABRAKAN.

Naskah utuh ada di atas. Teks KEDUA satuan yang diduga bertabrakan diulang di
bawah — keduanya wajib kamu baca sebelum menilai.

Tabrakan berarti keduanya tidak bisa berlaku bersamaan. Kalau ternyata bisa
— misalnya yang satu pengecualian yang sah bagi yang lain — gugurkan.

""" + _TAHAP4_ALAT + """

Kalau terbukti, tentukan satuan MANA yang menyimpang. Yang menyimpang itu
yang akan ditandai. Kalau tidak bisa ditentukan mana yang menyimpang, pilih
yang letaknya lebih belakang di dokumen.

Jawab dengan JSON:
{
  "terbukti": true/false,
  "satuan_ditandai": "<id satuan yang menyimpang>",
  "alasan": "<satu kalimat, dan SEBUTKAN kedua satuannya>",
  "teks_asli": "<potongan teks PERSIS dari satuan yang ditandai. Sependek
                 mungkin dan WAJIB berada dalam satu ayat. Label penomoran
                 seperti (1), a., atau 1. jangan ikut disalin>",
  "saran": "<satu kalimat saran. Kosongkan kalau kamu tidak tahu apa yang
             sebaiknya dilakukan>",
  "sasaran": "<DI MANA perbaikannya dikerjakan. WAJIB salah satu dari:
               'satuan ini' | 'pasal-1' | 'menimbang' | 'mengingat' |
               'menetapkan' | 'judul' | '<id satuan lain yang memang ada>'.
              Pada tabrakan, seringkali yang tepat justru id satuan satunya
              lagi. Jangan mengarang id>",
""" + _TAHAP4_TIDAK_ADA + """
  "skor": <0.0 sampai 1.0>
}"""


# ---------------------------------------------------------------------------
# KORPUS OPENSEARCH — F3-001 dan F3-003, dijalankan sesudah tahap 4
# ---------------------------------------------------------------------------

TAHAP6_PASTIKAN_ULANG = """Sebuah ketentuan diduga berpotensi bertentangan
dengan peraturan lain. Di bawah ini teks utuh ketentuannya DAN pembanding yang
ditemukan dari korpus peraturan.

PENTING: kamu HANYA boleh menyebut peraturan yang ada di daftar pembanding di
bawah. Jangan menyebut peraturan lain dari ingatanmu — sekalipun kamu yakin.

Teks pembanding berasal dari pemindaian yang OCR-nya bisa rusak. Kalau
kutipannya terbaca janggal, katakan tidak yakin.

Jawab dengan JSON:
{
  "terbukti": true/false,
  "peraturan": "<nama peraturan pembanding, salin dari daftar>",
  "alasan": "<satu kalimat. WAJIB memakai kata 'berpotensi bertentangan',
              bukan 'bertentangan' — temuan ini kemungkinan, bukan kesimpulan>",
  "teks_asli": "<potongan teks PERSIS dari rancangan yang diperiksa.
                SEPENDEK MUNGKIN — satu frasa atau satu ayat saja, JANGAN
                seluruh pasalnya. Kutipan yang merentang beberapa ayat tidak
                akan ketemu di naskah dan temuanmu gugur seluruhnya. Salin
                huruf demi huruf, termasuk tanda bacanya>",
  "saran": "<satu kalimat saran>",
  "skor": <0.0 sampai 1.0>
}"""


TAHAP6_RUMUSAN = """Sebuah kelemahan sudah TERBUKTI pada rancangan di bawah,
tetapi penggantinya belum diketahui. Di bawah ini juga ada rumusan dari
peraturan yang MASIH BERLAKU untuk hal serupa.

Tugasmu: usulkan pengganti untuk `teks_asli` SAJA, mencontoh cara peraturan
yang sudah berlaku merumuskannya.

EMPAT SYARAT, dan usulan yang melanggar salah satunya lebih baik dikosongkan:

  1. Penggantinya untuk `teks_asli` SAJA — bukan untuk kalimatnya, bukan untuk
     ayatnya. Bayangkan `teks_asli` dihapus dan tulisanmu ditaruh persis di
     tempatnya: kalimatnya harus jadi utuh dan benar, tanpa kata yang terulang.
     JANGAN mengulang kata-kata yang berada SEBELUM `teks_asli`.
  2. Panjangnya sepadan. Kalau perbaikannya menuntut menulis ulang kalimat yang
     jauh lebih panjang, KOSONGKAN — usulan begitu akan ditolak kode.
  3. Istilah yang sudah didefinisikan di Pasal 1 wajib dieja PERSIS.
  4. `peraturan` WAJIB disalin dari daftar di bawah. Jangan menyebut peraturan
     lain dari ingatanmu, sekalipun kamu yakin — kode memeriksanya, dan yang
     di luar daftar digugurkan seluruhnya.

Teks pembanding berasal dari pemindaian yang OCR-nya bisa rusak. Kalau
kutipannya terbaca janggal, jangan dijadikan contoh.

Mengosongkan `usulan_rumusan` adalah jawaban yang baik, bukan kegagalan.

Jawab dengan JSON:
{
  "usulan_rumusan": "<pengganti harfiah untuk teks_asli, atau string kosong>",
  "peraturan": "<nama peraturan yang kamu contoh, salin dari daftar.
                 Kosongkan kalau usulan_rumusan kosong>",
  "saran": "<satu kalimat untuk penelaah: apa yang diperbaiki dan kenapa>",
  "skor": <0.0 sampai 1.0, seberapa yakin usulanmu tepat>
}"""


def susun(instruksi: str, bahan: str) -> str:
    """Rangkai satu pesan korpus: aturan tetap, instruksi, lalu bahannya."""
    return f"{ATURAN_TETAP}\n\n{instruksi}\n\n---\n\n{bahan}"


def susun_dengan_bahan(bahan: str, tugas: str) -> str:
    """Rangkai satu pesan tahap 3/4: aturan tetap, NASKAH UTUH, lalu tugasnya.

    Naskahnya di DEPAN dan sama persis di tiap panggilan — awalan yang sama
    membuat potongan harga awalan prompt berlaku, dan tugas di belakang dibaca
    model sesudah naskahnya, bukan sebelum.
    """
    return f"{ATURAN_TETAP}\n\n---\n\n{bahan}\n\n---\n\n{tugas}"


def isi(templat: str, **nilai: str) -> str:
    """Isi templat tahap 3 ($jenis, $fokus, …). Kurung kurawal JSON aman."""
    return Template(templat).substitute(**nilai)
