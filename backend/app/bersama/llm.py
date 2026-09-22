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
yang sudah disiapkan, jadi seluruh Langkah 2–6 bisa diuji tanpa jaringan,
tanpa kredensial, dan tanpa biaya.
"""

from __future__ import annotations

import json
import re
from typing import Any, Optional, Protocol


class Jawaban:
    """Hasil satu panggilan, berikut ongkosnya."""

    def __init__(
        self, teks: str, token_masuk: int = 0, token_keluar: int = 0
    ) -> None:
        self.teks = teks
        self.token_masuk = token_masuk
        self.token_keluar = token_keluar


class Klien(Protocol):
    """Bentuk yang dipegang seluruh tahap. Aslinya maupun palsunya menuruti ini."""

    def tanya(self, peran: str, pesan: str) -> Jawaban: ...


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
    """baca_json + catat kegagalannya. Dipakai tahap 4 dan 6."""
    isi = baca_json(teks)
    if not isi:
        ongkos.gagal += 1
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

    def catat(self, j: Jawaban) -> None:
        self.panggilan += 1
        self.token_masuk += j.token_masuk
        self.token_keluar += j.token_keluar

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
    """Azure OpenAI. Kredensialnya dibaca dari core/config.py, bukan dari sini."""

    def __init__(self, batas_waktu: float = 60.0) -> None:
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
            )

    @property
    def siap(self) -> bool:
        return self._siap

    def tanya(self, peran: str, pesan: str) -> Jawaban:
        if not self._siap or self._klien is None:
            raise RuntimeError(
                "Azure OpenAI belum terkonfigurasi. Periksa lewat GET /cek-env."
            )
        resp = self._klien.chat.completions.create(
            model=self._deployment,
            messages=[
                {"role": "system", "content": peran},
                {"role": "user", "content": pesan},
            ],
            temperature=0,
        )
        isi = resp.choices[0].message.content if resp.choices else ""
        pakai = getattr(resp, "usage", None)
        return Jawaban(
            teks=isi or "",
            token_masuk=getattr(pakai, "prompt_tokens", 0) or 0,
            token_keluar=getattr(pakai, "completion_tokens", 0) or 0,
        )


# ---------------------------------------------------------------------------
# Klien palsu — supaya seluruh Fase 2 bisa dites tanpa biaya
# ---------------------------------------------------------------------------


class KlienPalsu:
    """Menjawab dari daftar yang sudah disiapkan, urut.

    Menyimpan tiap pesan yang diterimanya di `diminta`, sehingga tes bisa
    memeriksa APA yang dikirim ke model — misalnya memastikan konteks tetap
    benar-benar ikut, atau satuan yang dirujuk benar-benar dilampirkan.
    """

    def __init__(self, jawaban: list[str]) -> None:
        self._antrean = list(jawaban)
        self.diminta: list[tuple[str, str]] = []

    @property
    def siap(self) -> bool:
        return True

    def tanya(self, peran: str, pesan: str) -> Jawaban:
        self.diminta.append((peran, pesan))
        teks = self._antrean.pop(0) if self._antrean else "{}"
        return Jawaban(teks=teks, token_masuk=len(pesan) // 4, token_keluar=len(teks) // 4)


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
