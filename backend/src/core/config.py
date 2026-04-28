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

    # LLM (DashScope)
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_BASE_URL: str = ""

    # Chroma
    CHROMA_PERSIST_DIR: str = "chroma_db"

    # Database
    DATABASE_URL: str = ""


settings = Settings()
