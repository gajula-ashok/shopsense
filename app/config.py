from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 🗄️ Database Properties
    DATABASE_URL: str = "postgresql+psycopg2://postgres:ashok786@localhost:5432/shopsense"
    
    # 🔑 JWT Authentication Properties (Add these fields!)
    SECRET_KEY: str = "your-fallback-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
