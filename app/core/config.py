import os

from dynaconf import Dynaconf
from pydantic import BaseModel
from pathlib import Path

class DBConfig(BaseModel):
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

class APPConfig(BaseModel):
    app_port: int
    app_host: str
    app_version: str
    app_name: str
    app_mount: str
    environment: str

class FileStorageConfig(BaseModel):
    root_dir: str

class Settings(BaseModel):
    app: APPConfig
    db: DBConfig
    fileStorage: FileStorageConfig

dyna_settings = Dynaconf(
    settings_files=["settings.toml"],
)

settings = Settings(app=dyna_settings["app_settings"], db=dyna_settings["db_settings"], fileStorage=dyna_settings["file_storage_settings"])
#переопределить значение settings.toml, если переменная окружения DB_HOST определена
settings.db.db_host = os.environ.get("DB_HOST") or settings.db.db_host

def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent

def get_alembic_cfg_path() -> Path:
    return Path(os.path.join(get_project_root(),'alembic.ini'))

