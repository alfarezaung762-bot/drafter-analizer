"""Endpoint analisis — POST /analisis/jalankan.

Handler setipis mungkin: parse input → panggil fungsi → kembalikan JSON.
"""

from fastapi import APIRouter

from app.models.temuan import AnalisisRequest, AnalisisResponse
from app.rules.format_baku import jalankan_semua

router = APIRouter(prefix="/analisis", tags=["analisis"])


@router.post("/jalankan", response_model=AnalisisResponse)
async def jalankan_analisis(request: AnalisisRequest) -> AnalisisResponse:
    """Jalankan seluruh pemeriksaan format baku pada daftar paragraf."""
    temuan = jalankan_semua(request.paragraf, request.jenis_dokumen)
    return AnalisisResponse(
        temuan=temuan,
        jumlah_paragraf=len(request.paragraf),
    )
