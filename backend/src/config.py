from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "Chen-Assistant"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # LLM
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    LLM_MODEL: str = ""

    # Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530

    # Database
    DATABASE_URL: str = ""


settings = Settings()
