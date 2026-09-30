"""KlienAzure — ganti model cukup lewat .env.

Model penalaran (seri GPT-5: Terra, Luna) menolak temperature=0 dengan 400.
Klien wajib mengulang tanpa temperature, lalu berhenti mengirimnya; model
yang menerimanya (gpt-4.1) tetap mendapat temperature=0.
"""

from types import SimpleNamespace

import httpx
import openai
import pytest

from app.bersama.llm import KlienAzure

_TOLAK_SUHU = (
    "Unsupported value: 'temperature' does not support 0 with this model. "
    "Only the default (1) value is supported."
)


def _galat(status: int, pesan: str) -> Exception:
    kelas = {400: openai.BadRequestError, 429: openai.RateLimitError}[status]
    permintaan = httpx.Request("POST", "https://contoh.openai.azure.com")
    return kelas(pesan, response=httpx.Response(status, request=permintaan), body=None)


def _jawaban(teks: str = "ok"):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=teks, tool_calls=None))],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=1),
    )


class _Completions:
    def __init__(self, tolak_suhu: bool, galat_lain: Exception | None = None):
        self.tolak_suhu = tolak_suhu
        self.galat_lain = galat_lain
        self.permintaan: list[dict] = []

    def create(self, **kw):
        self.permintaan.append(kw)
        if self.galat_lain is not None:
            raise self.galat_lain
        if self.tolak_suhu and "temperature" in kw:
            raise _galat(400, _TOLAK_SUHU)
        return _jawaban()


def _klien(completions: _Completions) -> KlienAzure:
    k = KlienAzure.__new__(KlienAzure)
    k._deployment = "uji"
    k._siap = True
    k._pakai_suhu = True
    k._klien = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return k


def test_model_yang_menerima_suhu_tetap_dapat_temperature_0():
    c = _Completions(tolak_suhu=False)
    k = _klien(c)
    k.tanya("peran", "pesan")
    k.tanya("peran", "pesan")
    assert [p.get("temperature") for p in c.permintaan] == [0, 0]


def test_model_yang_menolak_suhu_diulang_tanpa_temperature_lalu_diingat():
    c = _Completions(tolak_suhu=True)
    k = _klien(c)
    assert k.tanya("peran", "pesan").teks == "ok"
    k.tanya("peran", "pesan")
    # Sekali ditolak, sekali diulang, lalu panggilan berikutnya langsung tanpa.
    assert ["temperature" in p for p in c.permintaan] == [True, False, False]


def test_panggilan_beralat_juga_diulang_tanpa_temperature():
    c = _Completions(tolak_suhu=True)
    k = _klien(c)
    alat = [{"type": "function", "function": {"name": "cari_teks", "parameters": {}}}]
    assert k.tanya_alat("peran", "pesan", alat, lambda nama, arg: "").teks == "ok"
    assert "temperature" not in c.permintaan[-1]
    assert c.permintaan[-1]["tools"] == alat


def test_galat_lain_tidak_ditelan():
    c = _Completions(tolak_suhu=False, galat_lain=_galat(429, "rate limit"))
    k = _klien(c)
    with pytest.raises(openai.RateLimitError):
        k.tanya("peran", "pesan")
    assert len(c.permintaan) == 1  # tidak diulang diam-diam
