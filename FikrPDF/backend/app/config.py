from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "FikrPDF"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    cors_origins: str = "http://localhost:3000"
    rate_limit_per_minute: int = 30
    log_level: str = "INFO"

    # Phase 5
    database_url: str = "postgresql+psycopg://postgres:Talha1234%23@localhost:5432/fikrpdf"

    storage_path: str = "./storage"

    # Tier limits (Gap 2)
    free_max_file_mb: int = 25
    pro_max_file_mb: int = 200
    free_daily_tasks: int = 5
    pro_daily_tasks: int = 1000

    # File lifecycle (Gap 1)
    free_ttl_hours: int = 2
    pro_ttl_hours: int = 24
    cleanup_interval_minutes: int = 15

 # Upload safety (Gap 4)
    max_decompressed_ratio: float = 100.0  # zip-bomb guard
    allowed_mimes: str = (
        "application/pdf,"
        "image/jpeg,image/png,image/webp,"
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document,"
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,"
        "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
    @property
    def allowed_mime_list(self) -> list[str]:
        return [m.strip() for m in self.allowed_mimes.split(",") if m.strip()]

    def max_size_bytes(self, tier: str = "free") -> int:
        mb = self.pro_max_file_mb if tier in ("pro", "business") else self.free_max_file_mb
        return mb * 1024 * 1024

    def ttl_hours(self, tier: str = "free") -> int:
        return self.pro_ttl_hours if tier in ("pro", "business") else self.free_ttl_hours


settings = Settings()