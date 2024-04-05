import uuid

from sqlalchemy import (
    Column,
    MetaData,
    Table,
    Text,
    UUID,
)


metadata_obj = MetaData()

texts_table = Table(
    "texts_table",
    metadata_obj,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("link", Text, nullable=False),
    Column("text", Text, nullable=False),
)
