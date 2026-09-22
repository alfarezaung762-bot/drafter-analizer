"""Tabel rujukan KMK 527 Lampiran II — statis.

Setiap aturan Fase 1 punya satu entri di sini. Butir dan kutipan TIDAK BOLEH
diambil dari OpenSearch maupun dari model — hanya dari naskah KMK 527 sendiri.

## Tiga tingkat keandalan

`status` menyatakan asal-usul isi entri, dan menentukan apa yang boleh
ditampilkan ke penelaah:

| `status` | Artinya | Di antarmuka |
|---|---|---|
| `"placeholder"` | Belum diisi sama sekali | "rujukan belum diverifikasi" |
| `"ekstraksi"` | Diisi dari ekstraksi teks PDF, belum dibaca visual | "rujukan belum diverifikasi" |
| `"visual"` | Sudah dibaca dan diketik ulang manusia dari naskah | tampil sebagai rujukan final |

## Riwayat verifikasi

**18 Sep 2026 — kelima entri dinaikkan ke `"visual"`.** Penelaah mengirim
pindaian halaman KMK 527 Lampiran II (halaman 30, 35, 36, dan 37) sebagai
gambar, bukan hasil ekstraksi teks. Tiap kutipan di bawah dicocokkan kata per
kata terhadap halaman itu, termasuk tanda bacanya.

Yang diperiksa dan hasilnya:

- butir 8 (hlm. 30) — cocok, termasuk keempat pengecualian huruf a–d
- butir 22 (hlm. 35) — **cocok, dan berbunyi "pada umumnya", bukan "wajib"**
- butir 23 (hlm. 35) — cocok
- butir 32 dan 33 (hlm. 36) — cocok, keduanya memang dibatasi ke dasar hukum
- butir 38 dan 39 (hlm. 37) — cocok, termasuk "tanpa frasa Republik Indonesia"

Sebelumnya isinya berstatus `"ekstraksi"`, diambil dari teks OCR yang korupsinya
khas dan mekanis: "clan" untuk "dan", "MENTER!" untuk "MENTERI", "REPU8LIK"
untuk "REPUBLIK", "spas1" untuk "spasi". Pindaian halaman menghilangkan
keraguan itu.

## Mengubah entri

Naikkan `status` ke `"visual"` HANYA setelah membaca butirnya dari naskah atau
pindaian halamannya, bukan dari ekstraksi teks. Jangan menaikkan status karena
kutipannya "kelihatan benar".
"""

RUJUKAN: dict[str, dict[str, object]] = {
    "F1-001": {
        "nama_aturan": "Judul ditulis kapital seluruhnya",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "8",
        "kutipan": (
            "Judul PMK atau KMK ditulis seluruhnya dengan huruf kapital yang "
            "diletakkan di tengah margin tanpa diakhiri tanda baca dan tidak "
            "boleh ditambah dengan singkatan atau akronim kecuali terdapat hal "
            "sebagai berikut: a. belum diserap dalam bahasa Indonesia atau "
            "belum ada padanan kata dalam bahasa Indonesia; b. merupakan "
            "istilah teknis yang baku; c. jika tidak disingkat dapat mengubah "
            "makna bahasa tersebut; dan/atau d. sudah merupakan istilah yang "
            "baku dan digunakan secara internasional."
        ),
        "halaman_pdf": 30,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Aturannya IMPERATIF — 'ditulis seluruhnya dengan huruf kapital'. "
            "F1-001 dimatikan bukan karena aturannya lemah, melainkan karena "
            "alat belum bisa membedakan huruf tersimpan dari huruf tertampil "
            "(gaya ALL CAPS). Lihat fase1 drafter.md bagian 6.10."
        ),
    },
    "F1-002": {
        "nama_aturan": "Judul pembuka konsisten dengan judul pada Menetapkan",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "39",
        "kutipan": (
            "Jenis dan nama yang tercantum dalam judul PMK atau KMK "
            "dicantumkan kembali setelah kata \"Menetapkan\", tanpa frasa "
            "\"Republik Indonesia\" serta ditulis seluruhnya dengan huruf "
            "kapital dan diakhiri dengan tanda baca titik (.)."
        ),
        "halaman_pdf": 37,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Aturannya IMPERATIF — 'dicantumkan kembali'. Frasa 'Republik "
            "Indonesia' memang sengaja dibuang di klausul Menetapkan; "
            "normalisasi di _ekstrak_judul_menetapkan() sudah memperhitungkan "
            "itu."
        ),
    },
    "F1-003": {
        "nama_aturan": "Kelengkapan Menimbang / Mengingat / Menetapkan",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "13, 16, 23, 37, 38",
        "kutipan": (
            "Butir 13: Pembukaan terdiri atas: a. Frasa Dengan Rahmat Tuhan "
            "Yang Maha Esa (khusus PMK); b. Jabatan pembentuk PMK atau KMK; "
            "c. Konsiderans; d. Dasar Hukum; dan e. Diktum. — "
            "Butir 16: Konsiderans diawali dengan kata \"Menimbang\" ... "
            "diakhiri dengan tanda baca titik dua (:). — "
            "Butir 23: Dasar hukum diawali dengan kata \"Mengingat\" ... "
            "diakhiri dengan tanda baca titik dua (:). — "
            "Butir 37: Diktum terdiri atas: a. kata \"Memutuskan\"; b. kata "
            "\"Menetapkan\"; dan c. jenis dan nama PMK atau KMK."
        ),
        "halaman_pdf": 33,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Butir 13 yang menetapkan kelima bagian pembukaan sebagai "
            "kerangka wajib; butir 16, 23, 37, dan 38 merinci tiap bagiannya."
        ),
    },
    "F1-004": {
        "nama_aturan": "Rumusan lazim butir Menimbang terakhir",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "22",
        "kutipan": (
            "Jika konsiderans Menimbang memuat lebih dari satu pertimbangan, "
            "rumusan butir pertimbangan terakhir PADA UMUMNYA berbunyi sebagai "
            "berikut: a. Konsiderans Menimbang PMK, berbunyi \"bahwa "
            "berdasarkan pertimbangan sebagaimana dimaksud dalam huruf ..., "
            "perlu menetapkan Peraturan Menteri Keuangan tentang ...\" dan "
            "diakhiri dengan tanda baca titik koma (;). b. Konsiderans "
            "Menimbang KMK, berbunyi \"bahwa berdasarkan pertimbangan "
            "sebagaimana dimaksud dalam huruf ..., perlu menetapkan Keputusan "
            "Menteri Keuangan tentang ...\" dan diakhiri dengan tanda baca "
            "titik koma (;)."
        ),
        "halaman_pdf": 35,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "PENTING — butir ini TIDAK IMPERATIF. Kata kuncinya 'pada "
            "umumnya', bukan 'wajib'. Penyimpangan dari rumusan ini belum "
            "tentu kesalahan, jadi F1-004 hanya boleh mengeluarkan CATATAN "
            "yang meminta penelaah menimbang, bukan menyatakan naskahnya "
            "salah. Dokumen pengetahuan proyek sempat menulis 'wajib "
            "berbunyi baku' — itu keliru dan sudah dikoreksi. "
            "Kata 'PADA UMUMNYA' di kutipan sengaja dikapitalkan agar "
            "pembaca berikutnya tidak melewatkannya."
        ),
    },
    "F1-005": {
        "nama_aturan": "Ejaan baku pada dasar hukum",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "32, 33",
        "kutipan": (
            "Butir 32: Penulisan judul peraturan perundang-undangan yang "
            "dijadikan dasar hukum, diawali dengan huruf kapital, kecuali kata "
            "\"tentang\" dan kata penghubung/konjungsi. — "
            "Butir 33: Jika terdapat dasar hukum berupa Undang-Undang, kedua "
            "huruf u ditulis dengan huruf kapital."
        ),
        "halaman_pdf": 36,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "PENTING — kedua butir dibatasi pada DASAR HUKUM (bagian "
            "Mengingat), bukan seluruh dokumen. Butir 32 berbunyi 'judul "
            "peraturan ... yang dijadikan dasar hukum'; butir 33 berbunyi "
            "'jika terdapat DASAR HUKUM berupa Undang-Undang'. Karena itu "
            "pemeriksaan 'Undang-Undang' dipersempit ke bagian Mengingat "
            "18 Sep 2026 — sebelumnya berlaku di seluruh dokumen dan salah "
            "menandai rujukan generik di dalam Lampiran. "
            "Butir 32 juga menyebut kata penghubung/konjungsi tetap huruf "
            "kecil; itu BELUM diperiksa alat."
        ),
    },
    # -----------------------------------------------------------------------
    # Ditambahkan 18 Sep 2026. Ketujuhnya dikutip dari pindaian halaman yang
    # sama, dan ketujuhnya IMPERATIF — berbeda dari F1-004.
    # -----------------------------------------------------------------------
    "F1-006": {
        "nama_aturan": "Judul tidak diakhiri tanda baca",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "8",
        "kutipan": (
            "Judul PMK atau KMK ditulis seluruhnya dengan huruf kapital yang "
            "diletakkan di tengah margin tanpa diakhiri tanda baca ..."
        ),
        "halaman_pdf": 30,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Butir yang sama dengan F1-001, tetapi bagian kalimat yang lain. "
            "F1-001 memeriksa kapitalnya (dimatikan); F1-006 memeriksa tanda "
            "bacanya, dan itu bisa dibuktikan dari teks tanpa perlu tahu gaya "
            "paragrafnya."
        ),
    },
    "F1-007": {
        "nama_aturan": "Penulisan kata \"Menimbang\"",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "16",
        "kutipan": (
            "Konsiderans diawali dengan kata \"Menimbang\" yang dicantumkan "
            "setelah jabatan pembentuk PMK atau KMK yang diletakkan di sebelah "
            "kiri margin, huruf awal ditulis dengan huruf kapital dan diakhiri "
            "dengan tanda baca titik dua (:)."
        ),
        "halaman_pdf": 34,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Pemeriksaan titik dua MEMILIH DIAM bila paragrafnya cuma berisi "
            "kata \"Menimbang\" sendirian — pada naskah bertabel titik duanya "
            "ada di sel sebelah dan tidak terbaca dari teks paragraf."
        ),
    },
    "F1-008": {
        "nama_aturan": "Bentuk tiap butir Menimbang",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "21",
        "kutipan": (
            "Tiap-tiap pokok pikiran diawali dengan huruf abjad dan dirumuskan "
            "dalam satu kalimat yang diawali dengan kata \"bahwa\" dan "
            "diakhiri dengan tanda baca titik koma (;)."
        ),
        "halaman_pdf": 34,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Potongan butir yang lebih pendek dari 15 karakter dilewati: itu "
            "hampir pasti hasil pemecahan yang gagal pada naskah bertabel, "
            "bukan butir yang benar-benar cacat."
        ),
    },
    "F1-009": {
        "nama_aturan": "Penulisan kata \"Mengingat\"",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "23",
        "kutipan": (
            "Dasar hukum diawali dengan kata \"Mengingat\" yang dicantumkan "
            "setelah konsiderans Menimbang yang diletakkan di sebelah kiri "
            "margin, huruf awal ditulis dengan huruf kapital dan diakhiri "
            "dengan tanda baca titik dua (:)."
        ),
        "halaman_pdf": 35,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": "Perilaku diamnya sama dengan F1-007.",
    },
    "F1-010": {
        "nama_aturan": "Penomoran dan tanda baca dasar hukum",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "31",
        "kutipan": (
            "Jika dasar hukum memuat lebih dari satu peraturan "
            "perundang-undangan, tiap dasar hukum diawali dengan angka Arab "
            "1, 2, 3, dan seterusnya, dan diakhiri dengan tanda baca titik "
            "koma (;)."
        ),
        "halaman_pdf": 36,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Paragraf dikelompokkan jadi butir lebih dahulu: sebuah butir "
            "dimulai di paragraf berangka dan berlanjut ke paragraf "
            "lanjutannya. Tanpa pengelompokan itu, judul peraturan panjang "
            "yang memenuhi beberapa paragraf akan dituduh melanggar di tiap "
            "lanjutannya. Aturannya juga diam bila tidak ada satu pun "
            "paragraf berangka — bisa jadi nomornya ada di sel tabel lain."
        ),
    },
    "F1-011": {
        "nama_aturan": "Penulisan kata \"Menetapkan\"",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "38",
        "kutipan": (
            "Kata \"Menetapkan\" dicantumkan setelah kata \"Memutuskan\" yang "
            "disejajarkan ke bawah dengan kata \"Menimbang\" dan kata "
            "\"Mengingat\". Huruf awal kata \"Menetapkan\" ditulis dengan huruf "
            "kapital dan diakhiri dengan tanda baca titik dua (:)."
        ),
        "halaman_pdf": 37,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Yang diperiksa baru penulisan katanya. Ketentuan \"disejajarkan "
            "ke bawah\" menyangkut tata letak, bukan teks, jadi tidak bisa "
            "diperiksa dari daftar paragraf."
        ),
    },
    "F1-012": {
        "nama_aturan": "Bentuk judul pada Menetapkan",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "39",
        "kutipan": (
            "Jenis dan nama yang tercantum dalam judul PMK atau KMK "
            "dicantumkan kembali setelah kata \"Menetapkan\", tanpa frasa "
            "\"Republik Indonesia\" serta ditulis seluruhnya dengan huruf "
            "kapital dan diakhiri dengan tanda baca titik (.)."
        ),
        "halaman_pdf": 37,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Butir yang sama dengan F1-002, bagian kalimat yang berbeda. "
            "F1-002 memeriksa kesamaan judulnya; F1-012 memeriksa tanda baca "
            "penutup dan ketiadaan frasa \"Republik Indonesia\". Bagian "
            "\"ditulis seluruhnya dengan huruf kapital\" BELUM diperiksa — "
            "kendalanya sama dengan F1-001, yaitu gaya ALL CAPS."
        ),
    },

    # -----------------------------------------------------------------------
    # FASE 2 — ditambahkan 22 Sep 2026.
    #
    # SELURUHNYA BERSTATUS "placeholder", DAN ITU DISENGAJA. Nomor butir dan
    # kutipannya belum dibaca manusia dari naskah KMK 527, jadi tidak boleh
    # ditulis seolah sudah pasti — CLAUDE.md butir 3. Selama placeholder,
    # panel menyalakan penanda "rujukan belum diverifikasi" pada tiap
    # temuannya, dan itu perilaku yang benar.
    #
    # Sebagian aturan Fase 2 memang TIDAK bersumber dari KMK 527 melainkan
    # dari logika dokumen (brief 8.11) — untuk yang begitu, `sumber` ditulis
    # apa adanya dan `butir` dibiarkan kosong, bukan dikarang.
    # -----------------------------------------------------------------------
    "F2-001": {
        "nama_aturan": "Rujukan antar-pasal menunjuk satuan yang ada",
        "sumber": "Logika dokumen — belum dikonfirmasi penelaah (brief 8.11)",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "status": "placeholder",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Brief 8.11 mencantumkan 'Rujukan sebagaimana dimaksud dalam "
            "Pasal N menunjuk pasal yang ada' sebagai kemungkinan pemeriksaan "
            "yang BELUM dikonfirmasi penelaah. Dibangun karena kesalahannya "
            "bisa dibuktikan mutlak dari pohon satuan, tanpa penafsiran."
        ),
    },
    "F2-003": {
        "nama_aturan": "Definisi di Pasal 1 dipakai di batang tubuh",
        "sumber": "Logika dokumen — belum dikonfirmasi penelaah (brief 8.11)",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "status": "placeholder",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": "Brief 8.11: 'Definisi yang tidak pernah dipakai'.",
    },
    "F2-004": {
        "nama_aturan": "Penomoran bertingkat tidak melompat atau berulang",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "status": "placeholder",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Lampiran II mengatur penomoran Pasal, ayat, huruf, dan angka. "
            "NOMOR BUTIRNYA BELUM DIBACA VISUAL — wajib diisi dari pindaian "
            "halaman sebelum status dinaikkan ke 'visual'."
        ),
    },
    "F2-007": {
        "nama_aturan": "Bilangan ditulis angka dan huruf yang cocok",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "status": "placeholder",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Bilangan ditulis dua kali: angka Arab lalu hurufnya dalam "
            "kurung — '30 (tiga puluh) hari'. Kalau keduanya tidak cocok, "
            "batas waktunya jadi mendua dan berakibat hukum. NOMOR BUTIRNYA "
            "BELUM DIBACA VISUAL."
        ),
    },

    # -----------------------------------------------------------------------
    # FASE 2 — JALUR PENALARAN (F2-1xx). Ditambahkan 22 Sep 2026.
    #
    # Nomornya sengaja melompat ke seratusan supaya terbaca sekali lihat:
    # F2-0xx dibuktikan kode, F2-1xx dibuktikan model. Penelaah berhak tahu
    # mana temuan yang kesalahannya pasti dan mana yang hasil penalaran.
    #
    # Seluruhnya bersumber pada prioritas mentor (brief bagian 4), BUKAN pada
    # satu butir KMK 527 tertentu. Itu ditulis apa adanya di `sumber` — yang
    # tidak ada butirnya tidak dikarang butirnya.
    # -----------------------------------------------------------------------
    "F2-101": {
        "nama_aturan": "Rumusan tidak berpotensi ditafsirkan dua arah",
        "sumber": "Prioritas penelaah — cara mendefinisikan ketentuan (brief bagian 4)",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "status": "placeholder",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Temuan HASIL PENALARAN MODEL, bukan kesalahan yang bisa "
            "dibuktikan kode. Sudah lewat Langkah 4 (dibaca pada teks utuh) "
            "dan Langkah 5 (kutipannya dibuktikan ada di naskah), tetapi "
            "penilaian 'bisa dibaca dua arah' tetap penilaian. Penelaah yang "
            "memutuskan."
        ),
    },
    "F2-102": {
        "nama_aturan": "Kewajiban menyebut tegas siapa pemikulnya",
        "sumber": "Prioritas penelaah — cara mendefinisikan ketentuan (brief bagian 4)",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "status": "placeholder",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Ketentuan yang mewajibkan sesuatu tanpa menyebut subjek yang "
            "memikulnya. Temuan hasil penalaran model."
        ),
    },
    "F2-103": {
        "nama_aturan": "Kata operasional tidak saling bertabrakan",
        "sumber": "Prioritas penelaah — cara mendefinisikan ketentuan (brief bagian 4)",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "status": "placeholder",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "wajib / harus / dapat / dilarang dalam satu ketentuan yang sama, "
            "sehingga tidak jelas apakah perbuatannya diwajibkan atau "
            "dibolehkan. Temuan hasil penalaran model."
        ),
    },
    "F2-104": {
        "nama_aturan": "Dua ketentuan tidak saling meniadakan",
        "sumber": "Prioritas penelaah — cara mendefinisikan ketentuan (brief bagian 4)",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "status": "placeholder",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Dua satuan yang tidak bisa berlaku bersamaan. Keduanya WAJIB "
            "dibaca utuh di Langkah 4 sebelum salah satunya ditandai — "
            "pengecualian yang sah sering menyerupai tabrakan."
        ),
    },
    "F2-105": {
        "nama_aturan": "Tujuan di Menimbang tercakup batang tubuh",
        "sumber": "Prioritas penelaah — cara mendefinisikan ketentuan (brief bagian 4)",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "status": "placeholder",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Maksud yang dinyatakan di konsiderans tetapi tidak ada "
            "ketentuannya di batang tubuh. Temuan hasil penalaran model."
        ),
    },

    # -----------------------------------------------------------------------
    # FASE 3 — pembanding dari korpus peraturan.
    #
    # Kutipan pembandingnya berasal dari indeks yang teksnya hasil pemindaian,
    # jadi statusnya TIDAK PERNAH "visual" — penanda "belum diverifikasi" di
    # panel memang harus menyala untuk tiap temuan Fase 3.
    # -----------------------------------------------------------------------
    "F3-001": {
        "nama_aturan": "Berpotensi bertentangan dengan peraturan lain",
        "sumber": "Korpus peraturan JDIH — kutipan dari pemindaian",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "status": "placeholder",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "Temuan ini KEMUNGKINAN, bukan kesimpulan — bahasanya wajib "
            "'berpotensi bertentangan'. Nama peraturan pembandingnya disalin "
            "dari hasil pencarian korpus dan diverifikasi kode di Langkah 5; "
            "model tidak boleh menyebut peraturan dari ingatannya."
        ),
    },
}


def rujukan_sudah_lengkap(aturan_id: str) -> bool:
    """Cek apakah rujukan sudah diverifikasi VISUAL oleh manusia.

    Status "ekstraksi" sengaja dihitung BELUM lengkap: isinya berasal dari
    teks OCR, dan gate legal di antarmuka tetap harus menyala sampai ada
    manusia yang membaca butirnya langsung dari naskah.
    """
    entri = RUJUKAN.get(aturan_id)
    if entri is None:
        return False
    return entri.get("status") == "visual"


def ambil_rujukan(aturan_id: str) -> dict[str, str]:
    """Ambil rujukan untuk aturan tertentu.

    Returns dict dengan key: sumber, butir, kutipan, pdf_url, status.

    `status` ikut dikirim karena antarmuka TIDAK BOLEH menilai keandalan
    rujukan dari ada-tidaknya isi. Sebelum 18 Sep 2026 gate legal menyala
    hanya bila butirnya masih "..."; begitu butirnya terisi dari ekstraksi
    OCR, gate itu mati sendiri padahal tidak ada manusia yang memverifikasi
    apa pun. Sekarang yang menentukan status, bukan keterisian.
    """
    entri = RUJUKAN.get(aturan_id)
    if entri is None:
        raise KeyError(f"Aturan {aturan_id} tidak ditemukan di tabel rujukan")
    return {
        "sumber": str(entri["sumber"]),
        "butir": str(entri["butir"]),
        "kutipan": str(entri["kutipan"]),
        "pdf_url": str(entri["pdf_url"]),
        "status": str(entri.get("status", "placeholder")),
    }
