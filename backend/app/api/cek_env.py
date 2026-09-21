"""Endpoint diagnostik — GET /cek-env.

Memeriksa apakah tiap layanan yang dibutuhkan Fase 2/3 sudah terkonfigurasi
dan dapat dihubungi.  Tidak pernah mengembalikan nilai rahasia — hanya status
dan petunjuk yang disamarkan.
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["diagnostik"])


# ───────────────────────── utilitas ──────────────────────────


def _mask(value: str) -> str:
    """Samarkan nilai: tampilkan 4 karakter awal + ***, atau '(kosong)'."""
    if not value:
        return "(kosong)"
    if len(value) <= 6:
        return value[:2] + "***"
    return value[:4] + "***"


def _var_summary(name: str, value: str) -> dict[str, Any]:
    """Rangkuman satu variabel: nama, apakah terisi, dan nilai tersamar."""
    return {
        "nama": name,
        "terisi": bool(value),
        "nilai_samaran": _mask(value),
    }


async def _with_timeout(coro, seconds: float = 10):
    """Jalankan coroutine dengan batas waktu."""
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        return None  # sentinel — ditangani pemanggil


# ──────────────────── pengecekan koneksi ─────────────────────


async def _cek_opensearch() -> dict[str, Any]:
    """Coba ping OpenSearch cluster dengan timeout ketat."""
    host = settings.OPENSEARCH_HOST
    port = str(settings.OPENSEARCH_PORT)
    user = settings.OPENSEARCH_USER
    password = settings.OPENSEARCH_PASSWORD
    index = settings.OPENSEARCH_INDEX
    emb_index = settings.OPENSEARCH_EMBEDDING_INDEX

    variabel = [
        _var_summary("OPENSEARCH_HOST", host),
        _var_summary("OPENSEARCH_PORT", port),
        _var_summary("OPENSEARCH_USER", user),
        _var_summary("OPENSEARCH_PASSWORD", password),
        _var_summary("OPENSEARCH_INDEX", index),
        _var_summary("OPENSEARCH_EMBEDDING_INDEX", emb_index),
    ]

    if not host:
        return {
            "layanan": "OpenSearch",
            "terhubung": False,
            "pesan": "OPENSEARCH_HOST belum diisi di .env",
            "variabel": variabel,
        }

    try:
        import httpx

        # Pakai httpx dengan timeout eksplisit dan url ber-port yang sudah divalidasi
        url = settings.opensearch_url
        auth = (user, password) if user else None

        async with httpx.AsyncClient(verify=False, timeout=8.0) as client:
            resp = await client.get(url, auth=auth)
            resp.raise_for_status()
            info = resp.json()

        cluster_name = info.get("cluster_name", "?")
        version = info.get("version", {}).get("number", "?")

        # Cek index — quick HEAD request
        index_ada = False
        emb_index_ada = False
        if index:
            try:
                async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                    r = await client.head(f"{url}/{index}", auth=auth)
                    index_ada = r.status_code == 200
            except Exception:
                pass
        if emb_index:
            try:
                async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                    r = await client.head(f"{url}/{emb_index}", auth=auth)
                    emb_index_ada = r.status_code == 200
            except Exception:
                pass

        return {
            "layanan": "OpenSearch",
            "terhubung": True,
            "pesan": f"Cluster \"{cluster_name}\" v{version}",
            "variabel": variabel,
            "detail": {
                "cluster_name": cluster_name,
                "version": version,
                "index_tersedia": index_ada,
                "embedding_index_tersedia": emb_index_ada,
            },
        }
    except Exception as e:
        return {
            "layanan": "OpenSearch",
            "terhubung": False,
            "pesan": f"Gagal terhubung: {type(e).__name__}: {e}",
            "variabel": variabel,
        }


async def _cek_azure_openai_chat() -> dict[str, Any]:
    """Coba kirim prompt sepele ke deployment chat Azure OpenAI."""
    endpoint = settings.AZURE_OPENAI_TASK_INSTANCE_NAME
    api_key = settings.AZURE_OPENAI_TASK_API_KEY
    api_version = settings.AZURE_OPENAI_TASK_API_VERSION
    deployment = settings.AZURE_OPENAI_TASK_DEPLOYMENT_NAME

    variabel = [
        _var_summary("AZURE_OPENAI_TASK_INSTANCE_NAME", endpoint),
        _var_summary("AZURE_OPENAI_TASK_API_KEY", api_key),
        _var_summary("AZURE_OPENAI_TASK_API_VERSION", api_version),
        _var_summary("AZURE_OPENAI_TASK_DEPLOYMENT_NAME", deployment),
    ]

    if not all([endpoint, api_key, deployment]):
        kosong = [v["nama"] for v in variabel if not v["terisi"]]
        return {
            "layanan": "Azure OpenAI - Chat",
            "terhubung": False,
            "pesan": f"Variabel belum diisi: {', '.join(kosong)}",
            "variabel": variabel,
        }

    try:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version or "2025-03-01-preview",
            timeout=10.0,
        )

        resp = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": "Jawab hanya: OK"}],
                max_tokens=5,
                temperature=0,
            )
        )
        jawaban = resp.choices[0].message.content.strip() if resp.choices else "?"

        return {
            "layanan": "Azure OpenAI - Chat",
            "terhubung": True,
            "pesan": f"Deployment \"{deployment}\" merespons: \"{jawaban}\"",
            "variabel": variabel,
            "detail": {
                "deployment": deployment,
                "model": resp.model if resp.model else "?",
            },
        }
    except Exception as e:
        return {
            "layanan": "Azure OpenAI - Chat",
            "terhubung": False,
            "pesan": f"Gagal: {type(e).__name__}: {e}",
            "variabel": variabel,
        }


async def _cek_azure_openai_embedding() -> dict[str, Any]:
    """Coba buat embedding dari teks pendek."""
    endpoint = settings.AZURE_OPENAI_EMBEDDING_INSTANCE_NAME
    api_key = settings.AZURE_OPENAI_EMBEDDING_API_KEY
    api_version = settings.AZURE_OPENAI_EMBEDDING_API_VERSION
    deployment = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME

    variabel = [
        _var_summary("AZURE_OPENAI_EMBEDDING_INSTANCE_NAME", endpoint),
        _var_summary("AZURE_OPENAI_EMBEDDING_API_KEY", api_key),
        _var_summary("AZURE_OPENAI_EMBEDDING_API_VERSION", api_version),
        _var_summary("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", deployment),
    ]

    if not all([endpoint, api_key, deployment]):
        kosong = [v["nama"] for v in variabel if not v["terisi"]]
        return {
            "layanan": "Azure OpenAI - Embedding",
            "terhubung": False,
            "pesan": f"Variabel belum diisi: {', '.join(kosong)}",
            "variabel": variabel,
        }

    try:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version or "2025-03-01-preview",
            timeout=10.0,
        )

        resp = await asyncio.to_thread(
            lambda: client.embeddings.create(
                model=deployment,
                input="tes koneksi",
            )
        )
        dimensi = len(resp.data[0].embedding) if resp.data else 0

        return {
            "layanan": "Azure OpenAI - Embedding",
            "terhubung": True,
            "pesan": f"Deployment \"{deployment}\" - dimensi vektor: {dimensi}",
            "variabel": variabel,
            "detail": {
                "deployment": deployment,
                "dimensi": dimensi,
            },
        }
    except Exception as e:
        return {
            "layanan": "Azure OpenAI - Embedding",
            "terhubung": False,
            "pesan": f"Gagal: {type(e).__name__}: {e}",
            "variabel": variabel,
        }


# ──────────────────────── endpoint ───────────────────────────


def _timeout_result(nama: str) -> dict[str, Any]:
    return {
        "layanan": nama,
        "terhubung": False,
        "pesan": "Timeout — server tidak merespons dalam 12 detik",
        "variabel": [],
    }


@router.get("/cek-env")
async def cek_env():
    """Jalankan semua pengecekan koneksi secara paralel dengan timeout per layanan."""

    # Tiap cek dibungkus timeout 12 detik supaya satu layanan yang hang
    # tidak memblokir seluruh endpoint
    hasil_raw = await asyncio.gather(
        _with_timeout(_cek_opensearch(), 12),
        _with_timeout(_cek_azure_openai_chat(), 12),
        _with_timeout(_cek_azure_openai_embedding(), 12),
        return_exceptions=True,
    )

    nama_layanan = ["OpenSearch", "Azure OpenAI - Chat", "Azure OpenAI - Embedding"]
    layanan_list: list[dict[str, Any]] = []

    for i, h in enumerate(hasil_raw):
        if h is None:
            # timeout
            layanan_list.append(_timeout_result(nama_layanan[i]))
        elif isinstance(h, Exception):
            layanan_list.append({
                "layanan": nama_layanan[i],
                "terhubung": False,
                "pesan": f"Error: {type(h).__name__}: {h}",
                "variabel": [],
            })
        else:
            layanan_list.append(h)

    semua_terhubung = all(s["terhubung"] for s in layanan_list)

    return {
        "semua_terhubung": semua_terhubung,
        "layanan": layanan_list,
    }
