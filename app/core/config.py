from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8002


class ApiPrefix(BaseModel):
    pass


class DataBaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class GigachatConfig(BaseModel):
    credentials: str
    scope: str
    ca_bundle_file: str = str(BASE_DIR / "certs" / "russian_trusted_root_ca.crt")


class BotConfig(BaseModel):
    token: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="APP_CONFIG__",
        env_nested_delimiter="__",
    )
    run: RunConfig = RunConfig()
    prefix: ApiPrefix = ApiPrefix()
    db: DataBaseConfig
    gigachat: GigachatConfig
    bot: BotConfig


settings = Settings()
