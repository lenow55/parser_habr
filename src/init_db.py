import logging
from sqlalchemy import URL, create_engine

from src.config import AppSettings
from src.db_metadata import metadata_obj
from src.log import conf_logger

config = AppSettings()

print(config.model_dump_json(indent=2))

conf_logger(logging.DEBUG)
sqlogger = logging.getLogger("sqlalchemy.engine")
sqlogger.setLevel(logging.DEBUG)

url_object = URL.create(
    config.dialect,
    username=config.db_user,
    password=config.db_password.get_secret_value(),
    host=config.db_host,
    database=config.db_name,
    port=config.db_port,
)

engine = create_engine(url_object)
metadata_obj.create_all(engine)
