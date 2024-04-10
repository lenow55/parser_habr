import logging
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import URL

from src.config import AppSettings
from src.db_metadata import metadata_obj
from src.log import conf_logger

conf_logger(logging.DEBUG)
sqlogger = logging.getLogger("sqlalchemy.engine")
sqlogger.setLevel(logging.DEBUG)

async def main(config: AppSettings):
    url_object = URL.create(
        config.dialect,
        username=config.db_user,
        password=config.db_password.get_secret_value(),
        host=config.db_host,
        database=config.db_name,
        port=config.db_port,
    )

    engine = create_async_engine(url_object, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(metadata_obj.drop_all)
        await conn.run_sync(metadata_obj.create_all)
    await engine.dispose()

if __name__ == "__main__":
    app_config = AppSettings()
    asyncio.run(main(app_config))
