import os
from typing import Tuple, Type
from typing_extensions import Annotated

from pydantic import Field, SecretStr
from pydantic.functional_validators import BeforeValidator
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

BASE_DIR = "./"


def convert_str2int(v):
    if isinstance(v, str):
        v = int(v)
    return v


IntMapStr = Annotated[int, BeforeValidator(convert_str2int)]


# Родительский объект с общими настройками.
class AdvancedBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        secrets_dir="/run/secrets",
    )


class AppSettings(AdvancedBaseSettings):
    dialect: str = Field(default="postgresql+psycopg2")
    db_host: str = Field(default="localhost")
    db_port: IntMapStr = Field(default=5432)
    db_user: str = Field(default="user")
    db_name: str = Field(default="db")
    db_password: SecretStr = Field(default="")
    file_links_params: str = Field(default="links_params.json")

    @property
    def db_connect_url(self) -> str:
        """
        полный url для подключения к postgresql
        """
        return f"{self.dialect}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(
        json_file=(
            os.path.join(BASE_DIR, "config.json"),
            os.path.join(BASE_DIR, "debug_config.json"),
        ),
        env_file=(
            os.path.join(BASE_DIR, ".env"),
            os.path.join(BASE_DIR, ".env.debug"),
            os.path.join(BASE_DIR, ".env.debug_host"),
        ),
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            JsonConfigSettingsSource(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )
