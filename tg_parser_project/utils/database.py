from sqlalchemy import (
    Table,
    Column,
    Integer,
    BigInteger,
    String,
    Boolean,
    Text,
    MetaData,
    DateTime,
    ForeignKey,
)
from databases import Database

from utils.config import DB_CONFIG

DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

database = Database(DATABASE_URL)
metadata = MetaData()

messages_table = Table(
    "messages",
    metadata,
    Column("msg_id", Integer, primary_key=True),
    Column("chat_id", BigInteger, primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.user_id")),
    Column("text", Text),
    Column("media_type", String),
    Column("reply_to_msg_id", Integer),
    Column("fwd_from_user_id", BigInteger),
    Column("views", Integer),
    Column("has_links", Boolean),
    Column("date", DateTime(timezone=True)),
)
