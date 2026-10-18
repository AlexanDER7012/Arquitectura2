from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Base de datos (Postgres, MySQL, SQLite...) ---
    DATABASE_URL: str

    # --- Seguridad del dispositivo ---
    DEVICE_TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()