from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY:str
    JWT_ALGORITHM:str
    JWT_TOKEN_EXPIRE_TIME:int=30
    REDIS_HOST:str = "localhost"
    REDIS_PORT:int = 6379

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


Config = Settings()