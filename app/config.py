from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # JWT Config
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    # Database Config
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()