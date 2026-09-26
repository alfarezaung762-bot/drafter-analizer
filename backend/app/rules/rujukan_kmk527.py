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
| `"turunan"` | Butirnya sudah dibaca visual, tetapi aturannya AKIBAT butir itu — bukan bunyinya | "dasar turunan" |
| `"visual"` | Sudah dibaca dan diketik ulang manusia dari naskah | tampil sebagai rujukan final |

## Kenapa `"turunan"` perlu ada

Ditambahkan 25 Sep 2026 sesudah butir-butirnya dibaca satu per satu. Sebagian
aturan benar dan berguna, tetapi tidak ada satu butir pun yang berbunyi
demikian — yang ada butir yang AKIBATNYA begitu.

Contohnya F2-001. Butir 54d berbunyi "Huruf awal kata 'pasal' yang digunakan
sebagai acuan ditulis dengan huruf kapital" — seluruhnya tentang kapitalisasi.
Ia tidak berkata rujukan wajib menunjuk pasal yang ada. Menuliskannya sebagai
`butir 54d` begitu saja berarti mengarang dasar hukum di komentar naskah
penelaah, dan itu dilarang CLAUDE.md butir 3.

Maka dipisah: butirnya tetap disebut supaya penelaah bisa menelusurinya, tetapi
statusnya mengatakan terang-terangan bahwa ini turunan. Penelaah yang menimbang
apakah turunannya sah.

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
    # FASE 2 — ditambahkan 22 Sep 2026, butirnya diverifikasi 25 Sep 2026.
    #
    # Keempatnya dibaca dari citra halaman PDF (tools/halaman_pdf.py), bukan
    # dari ekstraksi teks — CLAUDE.md butir 4. Halaman 40, 41, dan 45.
    #
    # HASILNYA TIDAK SERAGAM, dan itu yang penting: dua aturan punya butir yang
    # berbunyi persis demikian, dua lagi cuma AKIBAT sebuah butir. Yang kedua
    # diberi status "turunan", bukan dinaikkan jadi "visual".
    # -----------------------------------------------------------------------
    "F2-001": {
        "nama_aturan": "Rujukan antar-pasal menunjuk satuan yang ada",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II — turunan butir 54d dan 54h",
        "butir": "54d, 54h",
        "kutipan": (
            "54d. Huruf awal kata \"pasal\" yang digunakan sebagai acuan "
            "ditulis dengan huruf kapital. — 54h. Huruf awal kata \"ayat\" "
            "yang digunakan sebagai acuan ditulis dengan huruf kecil."
        ),
        "halaman_pdf": 40,
        "status": "turunan",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "DIBACA VISUAL 25 Sep 2026, halaman 40. Kedua butir itu mengatur "
            "KAPITALISASI acuan, bukan keberadaan yang diacu — tidak satu pun "
            "butir Lampiran II berbunyi 'rujukan wajib menunjuk pasal yang "
            "ada'. Aturan ini akibat wajar dari adanya acuan: acuan yang "
            "menunjuk pasal yang tidak ada tidak bisa dibaca siapa pun. "
            "Kesalahannya tetap dibuktikan mutlak dari pohon satuan."
        ),
    },
    "F2-003": {
        "nama_aturan": "Definisi di Pasal 1 dipakai di batang tubuh",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "61, dengan pengecualian butir 64",
        "kutipan": (
            "61. Kata atau istilah yang dimuat dalam ketentuan umum hanyalah "
            "kata atau istilah yang digunakan berulang-ulang di dalam pasal "
            "atau beberapa pasal selanjutnya. — 64. Jika suatu kata atau "
            "istilah hanya digunakan satu kali, namun kata atau istilah itu "
            "diperlukan pengertiannya untuk suatu bab, bagian, atau paragraf "
            "tertentu, kata atau istilah itu diberi definisi."
        ),
        "halaman_pdf": 45,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "DIBACA VISUAL 25 Sep 2026, halaman 45. Butir 61 menuntut istilah "
            "dipakai BERULANG; aturan ini sengaja lebih longgar dan baru "
            "berbunyi pada NOL kemunculan, supaya pengecualian butir 64 tidak "
            "pernah salah tandai. Pengecualian itu tetap tidak bisa dinilai "
            "kode — 'diperlukan pengertiannya untuk suatu bab' adalah "
            "penilaian penelaah, jadi butir 64 ikut disebut di komentar. "
            "BATAS YANG MASIH ADA: butir 67 menghitung kemunculan di lampiran "
            "juga, sementara parser belum membaca lampiran sama sekali."
        ),
    },
    "F2-004": {
        "nama_aturan": "Penomoran bertingkat tidak melompat atau berulang",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "54c, 54f, 54k-7",
        "kutipan": (
            "54c. Pasal diberi nomor urut dengan angka Arab dan huruf awal "
            "kata \"pasal\" ditulis dengan huruf kapital. — 54f. Ayat diberi "
            "nomor urut dengan angka Arab di antara tanda baca kurung ( ( ) ) "
            "tanpa diakhiri tanda baca titik (.). — 54k-7. pembagian rincian "
            "(dengan urutan makin kecil) ditulis dengan huruf abjad kecil "
            "yang diikuti dengan tanda baca titik (.), angka Arab diikuti "
            "dengan tanda baca titik (.), abjad kecil dengan tanda baca "
            "kurung tutup ( ) ), angka Arab dengan tanda baca kurung tutup "
            "( ) );"
        ),
        "halaman_pdf": 40,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "DIBACA VISUAL 25 Sep 2026, halaman 40 dan 41. Kata kuncinya "
            "\"nomor urut\": deret yang melompat atau berulang bukan lagi "
            "urut. Berlaku sama untuk Pasal (54c), ayat (54f), dan rincian "
            "bertingkat (54k-7)."
        ),
    },
    "F2-007": {
        "nama_aturan": "Bilangan ditulis angka dan huruf yang cocok",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "54j",
        "kutipan": (
            "54j. Penulisan bilangan dalam pasal atau ayat selain menggunakan "
            "angka arab diikuti dengan kata atau frasa yang ditulis di antara "
            "tanda baca kurung ( ( ) )."
        ),
        "halaman_pdf": 41,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "DIBACA VISUAL 25 Sep 2026, halaman 41. Butirnya mewajibkan "
            "bilangan ditulis dua kali — angka lalu hurufnya dalam kurung. "
            "Kalau keduanya tidak cocok, batas waktu atau jumlahnya jadi "
            "mendua dan berakibat hukum. Mana yang benar TIDAK ditentukan "
            "butir ini, jadi aturannya tidak pernah menghasilkan hijau."
        ),
    },

    # -----------------------------------------------------------------------
    # FASE 2 — JALUR PENALARAN (F2-1xx). Ditambahkan 22 Sep 2026.
    #
    # Nomornya sengaja melompat ke seratusan supaya terbaca sekali lihat:
    # F2-0xx dibuktikan kode, F2-1xx dibuktikan model. Penelaah berhak tahu
    # mana temuan yang kesalahannya pasti dan mana yang hasil penalaran.
    #
    # Butirnya ditelusuri 25 Sep 2026 dengan membaca citra halaman. Hasilnya
    # membelah kelompok ini jadi dua, dan pembelahannya jujur:
    #
    #   F2-101, F2-104, F2-105  ada butir yang AKIBATNYA begitu → "turunan"
    #   F2-102, F2-103          TIDAK ADA butirnya di Lampiran II → tetap
    #                           placeholder, dan itu bukan kelalaian melainkan
    #                           hasil pencarian. Lihat catatan masing-masing.
    # -----------------------------------------------------------------------
    "F2-101": {
        "nama_aturan": "Rumusan tidak berpotensi ditafsirkan dua arah",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II — turunan butir 66",
        "butir": "66",
        "kutipan": (
            "66. Karena batasan pengertian atau definisi, singkatan, atau "
            "akronim berfungsi untuk menjelaskan makna suatu kata atau istilah "
            "maka batasan pengertian atau definisi, singkatan, atau akronim "
            "tidak perlu diberi penjelasan, dan karena itu harus dirumuskan "
            "dengan lengkap dan jelas sehingga tidak menimbulkan pengertian "
            "ganda."
        ),
        "halaman_pdf": 46,
        "status": "turunan",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "DIBACA VISUAL 25 Sep 2026, halaman 46. Butir 66 melarang "
            "pengertian ganda, tetapi HANYA untuk definisi di ketentuan umum. "
            "Aturan ini memeriksa rumusan di seluruh batang tubuh, jadi di "
            "luar Pasal 1 ia turunan, bukan kutipan. Temuannya juga hasil "
            "penalaran model — sudah lewat Langkah 4 dan 5, tetapi penilaian "
            "'bisa dibaca dua arah' tetap penilaian."
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
            "DICARI 25 Sep 2026, TIDAK KETEMU. Lampiran II tidak memuat satu "
            "butir pun yang mewajibkan norma menyebut subjek pemikulnya — "
            "butir 54g hanya menuntut satu ayat memuat satu norma dalam satu "
            "kalimat utuh, bukan menuntut subjeknya tegas. Kekosongan ini "
            "dilaporkan ke penelaah, tidak ditambal dengan butir yang "
            "kebetulan mirip: rujukan yang dikarang lebih berbahaya daripada "
            "tidak ada rujukan. Penanda 'rujukan belum diverifikasi' tetap "
            "menyala, dan itu perilaku yang benar."
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
            "DICARI 25 Sep 2026, TIDAK KETEMU. Lampiran II mengatur kata "
            "penghubung dalam tabulasi (butir 54l-o) dan melarang beberapa "
            "frasa tertentu (butir 102, 123c), tetapi tidak mengatur "
            "benturan wajib/harus/dapat/dilarang di dalam satu ketentuan. "
            "Sama seperti F2-102: dilaporkan apa adanya, tidak ditambal."
        ),
    },
    "F2-104": {
        "nama_aturan": "Dua ketentuan tidak saling meniadakan",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II — turunan butir 54a dan 54g",
        "butir": "54a, 54g",
        "kutipan": (
            "54a. Pasal merupakan satuan aturan dalam PMK yang memuat satu "
            "norma dan dirumuskan dalam satu kalimat yang disusun secara "
            "singkat, jelas, dan lugas. Pasal juga merupakan satuan aturan "
            "dalam PMK yang dapat memuat sejumlah norma dalam beberapa ayat "
            "yang memiliki keterkaitan. Rumusan norma dalam ayat dirumuskan "
            "dalam satu kalimat satu ayat yang disusun secara singkat, jelas, "
            "dan lugas. — 54g. Satu ayat hanya memuat satu norma yang "
            "dirumuskan dalam satu kalimat utuh."
        ),
        "halaman_pdf": 39,
        "status": "turunan",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "DIBACA VISUAL 25 Sep 2026, halaman 39-40. Kedua butir menuntut "
            "satu norma per satuan; tidak satu pun berkata dua ketentuan "
            "tidak boleh saling meniadakan. Turunannya wajar — dua norma yang "
            "bertabrakan membuat naskahnya tidak bisa dijalankan — tetapi "
            "tetap turunan. Keduanya WAJIB dibaca utuh di Langkah 4 sebelum "
            "salah satunya ditandai: pengecualian yang sah sering menyerupai "
            "tabrakan."
        ),
    },
    "F2-105": {
        "nama_aturan": "Tujuan di Menimbang tercakup batang tubuh",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II — turunan butir 17 dan 19",
        "butir": "17, 19",
        "kutipan": (
            "17. Konsiderans memuat uraian singkat mengenai pokok-pokok "
            "pikiran yang menjadi pertimbangan dan alasan pembentukan PMK "
            "atau KMK. — 19. Jika PMK atau KMK merupakan pelaksanaan dari "
            "peraturan perundang-undangan yang lebih tinggi, dalam konsiderans "
            "Menimbang cukup memuat satu pertimbangan yang berisi uraian "
            "ringkas mengenai perlunya melaksanakan ketentuan pasal atau "
            "beberapa pasal dari peraturan perundang-undangan yang lebih "
            "tinggi yang memerintahkan pembentukan PMK atau KMK tersebut."
        ),
        "halaman_pdf": 34,
        "status": "turunan",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "DIBACA VISUAL 25 Sep 2026, halaman 34. Butir 17 dan 19 mengatur "
            "ISI konsiderans; tidak satu pun mewajibkan tiap maksud yang "
            "disebut di sana punya ketentuannya di batang tubuh. Turunannya "
            "wajar — konsiderans adalah alasan pembentukan, dan alasan yang "
            "tidak berbuah ketentuan menandakan ada yang terlewat — tetapi "
            "tetap turunan, dan temuannya hasil penalaran model."
        ),
    },

    # -----------------------------------------------------------------------
    # FASE 3 — pembanding dari korpus peraturan.
    #
    # DUA HAL YANG DULU TERCAMPUR, dipisah 25 Sep 2026.
    #
    # `status` di bawah menyatakan keandalan RUJUKAN KE KMK 527 — apakah
    # butirnya sudah dibaca manusia. Itu berbeda dari keandalan KUTIPAN
    # PEMBANDING yang datang dari korpus, yang teksnya hasil pemindaian dan
    # memang tidak pernah bisa dijamin.
    #
    # Sebelumnya keduanya dinyatakan lewat satu medan: status Fase 3 ditahan
    # di "placeholder" supaya penanda peringatan menyala. Akibatnya rujukan
    # yang SUDAH diverifikasi tetap dilaporkan belum — bohong ke arah
    # sebaliknya. Sekarang keandalan korpus disampaikan penanda "Fase 3" di
    # panel, yang keterangannya memang tentang itu.
    # -----------------------------------------------------------------------
    "F3-002": {
        "nama_aturan": "Dasar hukum di Mengingat masih berlaku",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II — turunan butir 28 dan 29",
        "butir": "28, 29",
        "kutipan": (
            "28. Tidak dicantumkan sebagai dasar hukum: a. dalam hal PMK atau "
            "KMK berkenaan akan dicabut dan dinyatakan tidak berlaku dalam "
            "bagian penutup; dan/atau b. KMK yang telah ditetapkan tetapi "
            "belum berlaku. — 29. PMK atau peraturan perundang-undangan yang "
            "telah diundangkan tetapi belum berlaku tidak dicantumkan sebagai "
            "dasar hukum."
        ),
        "halaman_pdf": 36,
        "status": "turunan",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "DIBACA VISUAL 25 Sep 2026, halaman 36, DAN HASILNYA MENGOREKSI "
            "dugaan awal. Butir 28 dan 29 melarang mencantumkan peraturan "
            "yang BELUM BERLAKU — bukan yang SUDAH DICABUT. Tidak satu pun "
            "butir Lampiran II melarang mencantumkan dasar hukum yang sudah "
            "dicabut, padahal itulah yang diperiksa aturan ini. Larangannya "
            "berdiri di atas asas umum, bukan di atas KMK 527, jadi statusnya "
            "turunan dan butirnya disebut apa adanya supaya penelaah bisa "
            "menimbang sendiri.\n"
            "\n"
            "TIDAK memanggil model sama sekali — status dibaca langsung dari "
            "korpus. Yang dilaporkan fakta, bukan penilaian. Tetap perlu "
            "diperiksa penelaah, karena status di korpus bisa tertinggal dari "
            "keadaan sebenarnya. Aturan ini MEMILIH DIAM pada empat keadaan — "
            "bentuk tidak dikenali, tidak ketemu, cocok ganda berstatus beda, "
            "dan status di luar Berlaku/Tidak Berlaku."
        ),
    },
    "F3-001": {
        "nama_aturan": "Berpotensi bertentangan dengan peraturan lain",
        "sumber": "KMK 527/KMK.01/2022 Lampiran III huruf C dan huruf E",
        "butir": "Lampiran III huruf C angka 3 dan 4; huruf E Syarat Substantif 2b",
        "kutipan": (
            "Huruf C angka 3 — Analisis dengan Peraturan Perundang-undangan "
            "yang Lebih Tinggi: a. Berisi penjelasan apakah materi muatan "
            "peraturan perundang-undangan tersebut tidak bertentangan dengan "
            "Pancasila, Undang-Undang Dasar Negara Republik Indonesia Tahun "
            "1945 dan peraturan perundang-undangan yang lebih tinggi. "
            "b. Analisis tidak sebatas pada peraturan perundang-undangan yang "
            "mengamanatkan penyusunan peraturan perundang-undangan dimaksud. "
            "— Huruf C angka 4 — Analisis dengan Peraturan Perundang-undangan "
            "yang Setingkat: a. Berisi penjelasan apakah materi muatan "
            "peraturan perundang-undangan tersebut tidak bertentangan dengan "
            "peraturan perundang-undangan yang setingkat. b. Analisis tidak "
            "sebatas pada PMK terkait, namun juga peraturan perundang-undangan "
            "terkait lainnya yang setingkat. — Huruf E Syarat Substantif 2b: "
            "Rancangan PMK tidak bertentangan dengan peraturan "
            "perundang-undangan yang lebih tinggi."
        ),
        "halaman_pdf": 89,
        "status": "visual",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "DIBACA VISUAL 25 Sep 2026, halaman 89 dan 93. Dasarnya ada di "
            "LAMPIRAN III, bukan Lampiran II — karena itu tidak ketemu saat "
            "butir 1-132 yang ditelusuri. Kalimat huruf C angka 3b dan 4b "
            "justru menjelaskan kenapa aturan ini perlu korpus: analisisnya "
            "WAJIB melampaui peraturan yang disebut di Mengingat, dan itu "
            "tidak mungkin dituntaskan manual.\n"
            "\n"
            "Syarat Substantif 2b berbunyi sama pada daftar periksa KMK "
            "(halaman 95), jadi dasarnya berlaku untuk kedua jenis naskah.\n"
            "\n"
            "BATASNYA: huruf E 2b menyebut peraturan yang LEBIH TINGGI, "
            "sementara aturan ini juga membandingkan ke peraturan setingkat. "
            "Yang setingkat bersandar pada huruf C angka 4.\n"
            "\n"
            "Temuan ini KEMUNGKINAN, bukan kesimpulan — bahasanya wajib "
            "'berpotensi bertentangan'. Nama peraturan pembandingnya disalin "
            "dari hasil pencarian korpus dan diverifikasi kode di Langkah 5; "
            "model tidak boleh menyebut peraturan dari ingatannya. Kutipan "
            "pembandingnya sendiri berasal dari pemindaian yang OCR-nya bisa "
            "rusak — itu keterbatasan KORPUS, bukan keterbatasan rujukan ini, "
            "dan penanda 'Fase 3' di panel yang menyampaikannya."
        ),
    },
    "F3-003": {
        "nama_aturan": "Usulan rumusan dari peraturan yang masih berlaku",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "62, 65",
        "kutipan": (
            "62. Apabila rumusan definisi dari suatu peraturan "
            "perundang-undangan dirumuskan kembali dalam PMK yang akan "
            "dibentuk, rumusan definisi tersebut harus sama dengan rumusan "
            "definisi dalam PMK yang mengatur permasalahan sejenis dan telah "
            "berlaku. — 65. Jika suatu batasan pengertian atau definisi perlu "
            "dikutip kembali di dalam ketentuan umum suatu peraturan "
            "pelaksanaan, rumusan batasan pengertian atau definisi di dalam "
            "peraturan pelaksanaan harus sama dengan rumusan batasan "
            "pengertian atau definisi yang terdapat di dalam peraturan lebih "
            "tinggi yang dilaksanakan tersebut."
        ),
        "halaman_pdf": 45,
        "status": "turunan",
        "pdf_url": "https://jdih.kemenkeu.go.id/",
        "catatan": (
            "DIBACA VISUAL 25 Sep 2026, halaman 45. Butir 62 dan 65 memang "
            "menyuruh menyamakan rumusan dengan peraturan yang telah berlaku "
            "— tetapi KHUSUS untuk definisi di ketentuan umum. Aturan ini "
            "memakai asas yang sama untuk rumusan di seluruh batang tubuh, "
            "jadi di luar definisi ia turunan.\n"
            "\n"
            "BUKAN aturan yang menghasilkan temuan sendiri. Ia melengkapi "
            "temuan penalaran yang sudah ada dengan usulan rumusan yang "
            "dicontoh dari peraturan yang masih berlaku, lalu nama peraturan "
            "itu ikut ke komentar. Inilah satu-satunya jalan temuan F2-1xx "
            "bisa jadi hijau: tanpa peraturan sumber, usulannya tetap turun "
            "jadi contoh rumusan di komentar. Berbiaya — satu embedding, satu "
            "kueri korpus, dan satu panggilan model per temuan, dibatasi 15 "
            "per dokumen."
        ),
    },
}


def rujukan_sudah_lengkap(aturan_id: str) -> bool:
    """Cek apakah rujukan sudah diverifikasi VISUAL oleh manusia.

    Status "ekstraksi" sengaja dihitung BELUM lengkap: isinya berasal dari
    teks OCR, dan gate legal di antarmuka tetap harus menyala sampai ada
    manusia yang membaca butirnya langsung dari naskah.

    Status "turunan" JUGA dihitung belum lengkap, meski butirnya sudah dibaca
    visual. Yang dibaca memang benar, tetapi aturannya akibat butir itu dan
    bukan bunyinya — dan penelaah berhak tahu bedanya sebelum memakai
    rujukannya sebagai dasar mengubah naskah.
    """
    entri = RUJUKAN.get(aturan_id)
    if entri is None:
        return False
    return entri.get("status") == "visual"


def rujukan_turunan(aturan_id: str) -> bool:
    """Butirnya sudah dibaca visual, tetapi aturannya AKIBAT butir itu."""
    entri = RUJUKAN.get(aturan_id)
    return entri is not None and entri.get("status") == "turunan"


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
