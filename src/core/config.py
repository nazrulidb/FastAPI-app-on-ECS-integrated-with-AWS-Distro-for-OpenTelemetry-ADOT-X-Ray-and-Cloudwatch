from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # This will look for .env, but won't crash if it's missing.
    # It will automatically prioritize OS Environment Variables (like from ECS) 
    # over the file.
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DATABASE_URL: str
    DEBUG: bool = False

settings = Settings()
