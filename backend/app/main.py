from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analisis import router as analisis_router

app = FastAPI(title="Drafter Analiser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analisis_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
