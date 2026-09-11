from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # OpenSearch
    OPENSEARCH_HOST: str = ""
    OPENSEARCH_USER: str = ""
    OPENSEARCH_PASSWORD: str = ""
    OPENSEARCH_INDEX: str = ""
    OPENSEARCH_EMBEDDING_INDEX: str = ""

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: str = ""
    AZURE_OPENAI_API_VERSION: str = ""
    AZURE_TASK_DEPLOYMENT: str = ""
    AZURE_EMBEDDING_DEPLOYMENT: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
