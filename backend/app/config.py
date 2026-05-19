from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./dev.db"

    # M1.1 auth substrate.
    frontend_origin: str = "http://localhost:5173"
    session_cookie_name: str = "session"
    session_ttl_hours: int = 12
    # Set False over plain HTTP (local dev); True in any deployed environment.
    cookie_secure: bool = True


settings = Settings()
