"""SATU-SATUNYA pintu ke Azure OpenAI.

CLAUDE.md: panggilan ke layanan luar dikumpulkan di satu lapisan, tidak
tersebar. Yang ditanggung di sini: batas waktu, percobaan ulang, pencatatan
biaya, pembatasan panggilan berbarengan, dan **penolakan keluaran yang
bentuknya tidak sesuai**.

Yang terakhir itu yang paling penting. Prompt yang meminta JSON TIDAK menjamin
dapat JSON — model membungkusnya dengan ```json, menambah kalimat pengantar,
atau menjawab prosa. Kalau tiap pemanggil menangani itu sendiri, tiap
pemanggil punya bugnya sendiri.

BISA DITES TANPA MEMANGGIL MODEL. `KlienPalsu` menjawab dari daftar jawaban
yang sudah disiapkan, jadi seluruh tahap 3–4 bisa diuji tanpa jaringan,
tanpa kredensial, dan tanpa biaya — termasuk pemakaian alat.
"""

from __future__ import annotations

import json
import re
import threading
from typing import Any, Callable, Optional, Protocol

# Satu blok percakapan: (siapa, isi) — "system", "user", "AI memanggil alat",
# "hasil alat (dibaca AI)". Inilah yang ditulis Ekspor Tahap 3 dan 4.
Blok = tuple[str, str]

# Pelaksana alat: (nama alat, argumen) → teks hasil yang dibaca model.
PelaksanaAlat = Callable[[str, dict], str]


class Jawaban:
    """Hasil satu panggilan, berikut ongkosnya."""

    def __init__(
        self,
        teks: str,
        token_masuk: int = 0,
        token_keluar: int = 0,
        percakapan: Optional[list[Blok]] = None,
    ) -> None:
        self.teks = teks
        self.token_masuk = token_masuk
        self.token_keluar = token_keluar
        # Seluruh yang dibaca model dalam panggilan ini, urut — termasuk hasil
        # alat. Kosong untuk panggilan tanpa alat: isinya cukup (peran, pesan).
        self.percakapan = percakapan or []


class Klien(Protocol):
    """Bentuk yang dipegang seluruh tahap. Aslinya maupun palsunya menuruti ini."""

    def tanya(self, peran: str, pesan: str) -> Jawaban: ...


def tanya_dengan_alat(
    klien: Klien,
    peran: str,
    pesan: str,
    alat: list[dict],
    jalankan: PelaksanaAlat,
    batas_putaran: int = 4,
) -> Jawaban:
    """Tanya dengan alat bila klien mendukungnya; kalau tidak, tanya biasa.

    Jawaban yang kembali selalu membawa percakapannya — system, user, dan tiap
    pemanggilan alat berikut hasilnya — supaya Ekspor Tahap 4 bisa menulis apa
    yang benar-benar dibaca model.
    """
    penanya = getattr(klien, "tanya_alat", None)
    if alat and callable(penanya):
        return penanya(peran, pesan, alat, jalankan, batas_putaran)
    jawab = klien.tanya(peran, pesan)
    if not jawab.percakapan:
        jawab.percakapan = [("system", peran), ("user", pesan)]
    return jawab


# ---------------------------------------------------------------------------
# Membaca JSON dari keluaran model
# ---------------------------------------------------------------------------

_PAGAR = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def baca_json(teks: str) -> Optional[dict[str, Any]]:
    """Ambil objek JSON dari jawaban model. None kalau tidak bisa.

    Mengembalikan None — bukan menebak, bukan memperbaiki sebagian — supaya
    pemanggil bisa memilih diam. Keluaran yang tidak terbaca artinya kita
    tidak tahu apa yang dimaksud model, dan tidak tahu berarti tidak menuduh.
    """
    if not teks:
        return None

    calon = teks.strip()
    if m := _PAGAR.search(calon):
        calon = m.group(1).strip()

    try:
        hasil = json.loads(calon)
        return hasil if isinstance(hasil, dict) else None
    except json.JSONDecodeError:
        pass

    # Jawaban berprosa yang menyelipkan JSON di tengahnya.
    mulai, akhir = calon.find("{"), calon.rfind("}")
    if mulai == -1 or akhir <= mulai:
        return None
    try:
        hasil = json.loads(calon[mulai : akhir + 1])
        return hasil if isinstance(hasil, dict) else None
    except json.JSONDecodeError:
        return None



def skor_sah(nilai: object) -> float:
    """Baca skor keyakinan model, dijepit ke 0.0–1.0.

    Model bisa menjawab "0.9", 0.9, "tinggi", atau tidak menjawab sama sekali.
    Yang tidak terbaca jadi 0.0 — artinya gugur di ambang Langkah 5, bukan
    lolos. Ketidaktahuan tidak boleh menguntungkan tuduhan.
    """
    try:
        skor = float(nilai)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    return min(1.0, max(0.0, skor))


def baca_jawaban(teks: str, ongkos: "Ongkos") -> Optional[dict[str, Any]]:
    """baca_json + catat kegagalannya. Dipakai tahap 3, 4, dan korpus."""
    isi = baca_json(teks)
    if not isi:
        ongkos.catat_gagal()
        return None
    return isi


# ---------------------------------------------------------------------------
# Pencatat biaya
# ---------------------------------------------------------------------------


class Ongkos:
    """Berapa panggilan dan berapa token sudah dipakai satu analisis.

    Brief menyebut Law Analyzer menghabiskan ~Rp7,5 juta/bulan. Angka itu
    harus bisa diramalkan, bukan ditemukan di tagihan — jadi dicatat sejak
    panggilan pertama.
    """

    def __init__(self) -> None:
        self.panggilan = 0
        self.token_masuk = 0
        self.token_keluar = 0
        self.gagal = 0
        # Tahap 3 dan 4 boleh memanggil model berbarengan; penjumlahan dari
        # beberapa utas tanpa kunci bisa kehilangan hitungan.
        self._kunci = threading.Lock()

    def catat(self, j: Jawaban) -> None:
        with self._kunci:
            self.panggilan += 1
            self.token_masuk += j.token_masuk
            self.token_keluar += j.token_keluar

    def catat_gagal(self) -> None:
        with self._kunci:
            self.gagal += 1

    def ringkas(self) -> str:
        return (
            f"{self.panggilan} panggilan, "
            f"{self.token_masuk} token masuk, {self.token_keluar} keluar"
            + (f", {self.gagal} gagal" if self.gagal else "")
        )


# ---------------------------------------------------------------------------
# Klien sungguhan
# ---------------------------------------------------------------------------


class KlienAzure:
    """Azure OpenAI. Kredensialnya dibaca dari core/config.py, bukan dari sini.

    Batas waktu 180 detik dan enam kali coba ulang: sejak bug 7 tiap panggilan
    membawa naskah utuh (PMK 119 ±53 ribu token), jadi satu jawaban bisa lebih
    lama dari satu menit, dan kuota token per menit deployment lebih mudah
    tersentuh. Coba ulangnya ditangani SDK — jeda bertambah dan menuruti
    Retry-After dari Azure.
    """

    def __init__(self, batas_waktu: float = 180.0, coba_ulang: int = 6) -> None:
        from app.core.config import settings

        self._deployment = settings.AZURE_OPENAI_TASK_DEPLOYMENT_NAME
        self._siap = bool(
            settings.AZURE_OPENAI_TASK_INSTANCE_NAME
            and settings.AZURE_OPENAI_TASK_API_KEY
            and self._deployment
        )
        self._klien = None
        if self._siap:
            from openai import AzureOpenAI

            self._klien = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_TASK_INSTANCE_NAME,
                api_key=settings.AZURE_OPENAI_TASK_API_KEY,
                api_version=settings.AZURE_OPENAI_TASK_API_VERSION
                or "2025-03-01-preview",
                timeout=batas_waktu,
                max_retries=coba_ulang,
            )
        # temperature=0 supaya jawabannya konsisten. Model penalaran (seri
        # GPT-5 — Terra, Luna) menolaknya dengan 400 "Only the default (1)
        # value is supported"; begitu ditolak sekali, klien berhenti
        # mengirimnya. Ganti model cukup lewat .env.
        self._pakai_suhu = True

    def _buat(self, **permintaan: Any) -> Any:
        """chat.completions.create, dengan temperature=0 bila model menerimanya."""
        if self._pakai_suhu:
            try:
                return self._klien.chat.completions.create(temperature=0, **permintaan)
            except Exception as e:  # openai.BadRequestError
                if "temperature" not in str(e) or getattr(e, "status_code", None) != 400:
                    raise
                self._pakai_suhu = False
        return self._klien.chat.completions.create(**permintaan)

    @property
    def siap(self) -> bool:
        return self._siap

    def _pastikan_siap(self) -> None:
        if not self._siap or self._klien is None:
            raise RuntimeError(
                "Azure OpenAI belum terkonfigurasi. Periksa lewat GET /cek-env."
            )

    def tanya(self, peran: str, pesan: str) -> Jawaban:
        self._pastikan_siap()
        resp = self._buat(
            model=self._deployment,
            messages=[
                {"role": "system", "content": peran},
                {"role": "user", "content": pesan},
            ],
        )
        isi = resp.choices[0].message.content if resp.choices else ""
        pakai = getattr(resp, "usage", None)
        return Jawaban(
            teks=isi or "",
            token_masuk=getattr(pakai, "prompt_tokens", 0) or 0,
            token_keluar=getattr(pakai, "completion_tokens", 0) or 0,
        )

    def tanya_alat(
        self,
        peran: str,
        pesan: str,
        alat: list[dict],
        jalankan: PelaksanaAlat,
        batas_putaran: int = 4,
    ) -> Jawaban:
        """Tanya, dan jalankan alat yang diminta model sampai ia menjawab.

        Putaran terakhir memaksa jawaban (`tool_choice="none"`): model yang
        terus meminta alat tidak boleh membuat analisis menggantung.
        """
        self._pastikan_siap()
        pesan_api: list[dict] = [
            {"role": "system", "content": peran},
            {"role": "user", "content": pesan},
        ]
        percakapan: list[Blok] = [("system", peran), ("user", pesan)]
        masuk = keluar = 0
        for putaran in range(batas_putaran + 1):
            resp = self._buat(
                model=self._deployment,
                messages=pesan_api,
                tools=alat,
                tool_choice="auto" if putaran < batas_putaran else "none",
            )
            pakai = getattr(resp, "usage", None)
            masuk += getattr(pakai, "prompt_tokens", 0) or 0
            keluar += getattr(pakai, "completion_tokens", 0) or 0
            pesan_model = resp.choices[0].message if resp.choices else None
            minta = list(getattr(pesan_model, "tool_calls", None) or [])
            if pesan_model is None or not minta or putaran == batas_putaran:
                teks = (pesan_model.content if pesan_model else "") or ""
                return Jawaban(teks, masuk, keluar, percakapan)
            pesan_api.append(
                {
                    "role": "assistant",
                    "content": pesan_model.content,
                    "tool_calls": [
                        {
                            "id": m.id,
                            "type": "function",
                            "function": {
                                "name": m.function.name,
                                "arguments": m.function.arguments,
                            },
                        }
                        for m in minta
                    ],
                }
            )
            for m in minta:
                try:
                    argumen = json.loads(m.function.arguments or "{}")
                except json.JSONDecodeError:
                    argumen = {}
                if not isinstance(argumen, dict):
                    argumen = {}
                hasil = jalankan(m.function.name, argumen)
                percakapan.append(
                    ("AI memanggil alat", f"{m.function.name}({json.dumps(argumen, ensure_ascii=False)})")
                )
                percakapan.append(("hasil alat (dibaca AI)", hasil))
                pesan_api.append({"role": "tool", "tool_call_id": m.id, "content": hasil})
        return Jawaban("", masuk, keluar, percakapan)  # tidak tercapai


# ---------------------------------------------------------------------------
# Klien palsu — supaya seluruh Fase 2 bisa dites tanpa biaya
# ---------------------------------------------------------------------------


class KlienPalsu:
    """Menjawab dari daftar yang sudah disiapkan, urut.

    Menyimpan tiap pesan yang diterimanya di `diminta`, sehingga tes bisa
    memeriksa APA yang dikirim ke model — misalnya memastikan naskah utuh
    benar-benar ikut, atau satuan yang dirujuk benar-benar dilampirkan.

    Untuk panggilan beralat, butir antrean boleh berupa permintaan alat:
    `{"alat": "cari_teks", "argumen": {"teks": "Lampiran II"}}`. Butir-butir
    itu dijalankan berurutan sampai ketemu jawaban biasa (string).
    """

    def __init__(self, jawaban: list) -> None:
        self._antrean = list(jawaban)
        self.diminta: list[tuple[str, str]] = []
        self._kunci = threading.Lock()

    @property
    def siap(self) -> bool:
        return True

    def _ambil(self):
        with self._kunci:
            return self._antrean.pop(0) if self._antrean else "{}"

    def tanya(self, peran: str, pesan: str) -> Jawaban:
        with self._kunci:
            self.diminta.append((peran, pesan))
        teks = self._ambil()
        if isinstance(teks, dict):
            teks = "{}"  # permintaan alat di panggilan tanpa alat — tak terjawab
        return Jawaban(teks=teks, token_masuk=len(pesan) // 4, token_keluar=len(teks) // 4)

    def tanya_alat(
        self,
        peran: str,
        pesan: str,
        alat: list[dict],
        jalankan: PelaksanaAlat,
        batas_putaran: int = 4,
    ) -> Jawaban:
        with self._kunci:
            self.diminta.append((peran, pesan))
        percakapan: list[Blok] = [("system", peran), ("user", pesan)]
        butir = self._ambil()
        putaran = 0
        while isinstance(butir, dict) and putaran < batas_putaran:
            nama, argumen = str(butir.get("alat", "")), dict(butir.get("argumen") or {})
            percakapan.append(("AI memanggil alat", f"{nama}({json.dumps(argumen, ensure_ascii=False)})"))
            percakapan.append(("hasil alat (dibaca AI)", jalankan(nama, argumen)))
            putaran += 1
            butir = self._ambil()
        teks = butir if isinstance(butir, str) else "{}"
        return Jawaban(teks, len(pesan) // 4, len(teks) // 4, percakapan)


# ---------------------------------------------------------------------------
# Embedding — dipakai Fase 3 untuk mencari pembanding di korpus
# ---------------------------------------------------------------------------


class Perapal(Protocol):
    """Pengubah teks jadi vektor. Aslinya maupun palsunya menuruti ini."""

    def rapalkan(self, teks: str) -> list[float]: ...


class PerapalAzure:
    """Deployment embedding Azure OpenAI. 1536 dimensi (emb3small).

    Dipisah dari KlienAzure karena deployment-nya memang berbeda, lengkap
    dengan kunci dan versi API sendiri di core/config.py.
    """

    def __init__(self, batas_waktu: float = 30.0) -> None:
        from app.core.config import settings

        self._deployment = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME
        self._siap = bool(
            settings.AZURE_OPENAI_EMBEDDING_INSTANCE_NAME
            and settings.AZURE_OPENAI_EMBEDDING_API_KEY
            and self._deployment
        )
        self._klien = None
        if self._siap:
            from openai import AzureOpenAI

            self._klien = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_EMBEDDING_INSTANCE_NAME,
                api_key=settings.AZURE_OPENAI_EMBEDDING_API_KEY,
                api_version=settings.AZURE_OPENAI_EMBEDDING_API_VERSION
                or "2023-05-15",
                timeout=batas_waktu,
            )

    @property
    def siap(self) -> bool:
        return self._siap

    def rapalkan(self, teks: str) -> list[float]:
        if not self._siap or self._klien is None:
            raise RuntimeError(
                "Deployment embedding belum terkonfigurasi. Periksa lewat GET /cek-env."
            )
        resp = self._klien.embeddings.create(model=self._deployment, input=teks)
        return list(resp.data[0].embedding) if resp.data else []


class PerapalPalsu:
    """Vektor tetap, supaya Fase 3 bisa dites tanpa memanggil Azure."""

    def __init__(self, dimensi: int = 1536) -> None:
        self._dimensi = dimensi
        self.diminta: list[str] = []

    @property
    def siap(self) -> bool:
        return True

    def rapalkan(self, teks: str) -> list[float]:
        self.diminta.append(teks)
        return [0.0] * self._dimensi
