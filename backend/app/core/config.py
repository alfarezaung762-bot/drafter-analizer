from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenSearch
    OPENSEARCH_HOST: str = ""
    OPENSEARCH_PORT: int = 9200
    OPENSEARCH_USER: str = ""
    OPENSEARCH_PASSWORD: str = ""
    OPENSEARCH_INDEX: str = ""
    OPENSEARCH_EMBEDDING_INDEX: str = ""
    OPENSEARCH_EMBEDDING_SCHEMA: str = "new"

    # Azure OpenAI — Task (chat / reasoning)
    AZURE_OPENAI_TASK_DEPLOYMENT_NAME: str = ""
    AZURE_OPENAI_TASK_INSTANCE_NAME: str = ""
    AZURE_OPENAI_TASK_API_KEY: str = ""
    AZURE_OPENAI_TASK_API_VERSION: str = ""

    # Azure OpenAI — Embedding
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str = ""
    AZURE_OPENAI_EMBEDDING_INSTANCE_NAME: str = ""
    AZURE_OPENAI_EMBEDDING_API_KEY: str = ""
    AZURE_OPENAI_EMBEDDING_API_VERSION: str = ""

    @property
    def opensearch_url(self) -> str:
        if not self.OPENSEARCH_HOST:
            return ""
        host = self.OPENSEARCH_HOST.strip().rstrip("/")
        if not host.startswith(("http://", "https://")):
            host = f"https://{host}"
        if host.startswith("http://jdih-os") or "jdih-os" in host:
            host = host.replace("http://", "https://")
        import re
        if not re.search(r":\d+$", host):
            host = f"{host}:{self.OPENSEARCH_PORT}"
        return host

    # Fase 2/3 — basis data hasil per satuan (Neon Postgres)
    DATABASE_URL: str = ""

    # Fase 2 — angka penyetelan. Nilainya ditetapkan setelah diukur pada
    # dokumen nyata, dan ikut berubah kalau modelnya diganti.
    FASE2_SATUAN_PER_PANGGILAN: int = 6
    FASE2_PANGGILAN_BERBARENGAN: int = 4
    FASE2_AMBANG_SKOR: float = 0.7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
