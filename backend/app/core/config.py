from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "stock-report-hub"
    ENV: str = "dev"

    DATABASE_URL: str = "sqlite:///./data/app.sqlite3"

    USER_AGENT: str = "Mozilla/5.0"
    RATE_LIMIT_REQUESTS_PER_MIN: int = 30
    REQUEST_TIMEOUT_SECONDS: int = 20

    NAVER_MOBILE_RESEARCH_URLS: str = ""
    PDF_URLS: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

settings = Settings()
