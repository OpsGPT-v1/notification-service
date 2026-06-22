from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://opsgpt_user:opsgpt_password@opsgpt-db:5432/opsgpt_db"
    notification_channel: str = "console"
    slack_webhook_url: str = ""
    notification_retry_count: int = 3
    notification_timeout_seconds: int = 10
    app_env: str = "development"
    cors_origins: str = "*"
    db_init_max_attempts: int = 30
    db_init_delay_seconds: int = 2

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
