import psycopg2
from psycopg2.extras import execute_values
from utils.config import DB_CONFIG
from sqlalchemy import select, func
from .database import messages_table, database


def insert_messages(chat_id, messages: list[dict]):
    if not messages:
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    user_rows = []
    for msg in messages:
        u = msg["user"]
        user_rows.append(
            (
                u["user_id"],
                u["username"],
                u["first_name"],
                u["last_name"],
                u["phone"],
                u["lang_code"],
                u["is_verified"],
                u["is_scam"],
                u["status"],
            )
        )

    execute_values(
        cur,
        """
        INSERT INTO users (user_id, username, first_name, last_name, phone, lang_code, is_verified, is_scam, status)
        VALUES %s
        ON CONFLICT (user_id) DO NOTHING;
    """,
        user_rows,
    )

    msg_rows = []
    for msg in messages:
        msg_rows.append(
            (
                msg["msg_id"],
                chat_id,
                msg["user"]["user_id"],
                msg["text"],
                msg["media_type"],
                msg["reply_to_msg_id"],
                msg["fwd_from_user_id"],
                msg["views"],
                msg["has_links"],
                msg["date"],
            )
        )

    execute_values(
        cur,
        """
        INSERT INTO messages (msg_id, chat_id, user_id, text, media_type, reply_to_msg_id, fwd_from_user_id, views, has_links, date)
        VALUES %s
        ON CONFLICT (msg_id, chat_id) DO NOTHING;
    """,
        msg_rows,
    )

    react_rows = []
    for msg in messages:
        for r in msg["reactions"]:
            react_rows.append((msg["msg_id"], chat_id, r))

    if react_rows:
        execute_values(
            cur,
            """
            INSERT INTO reactions (msg_id, chat_id, reaction)
            VALUES %s
            ON CONFLICT DO NOTHING;
        """,
            react_rows,
        )

    mention_rows = []
    for msg in messages:
        for m in msg["mentions"]:
            mention_rows.append((msg["msg_id"], chat_id, m))

    if mention_rows:
        execute_values(
            cur,
            """
            INSERT INTO mentions (msg_id, chat_id, mention)
            VALUES %s
            ON CONFLICT DO NOTHING;
        """,
            mention_rows,
        )

    conn.commit()
    cur.close()
    conn.close()


async def get_min_max_message_dates(chat_id: int):
    query = select(
        func.min(messages_table.c.date), func.max(messages_table.c.date)
    ).where(messages_table.c.chat_id == chat_id)
    result = await database.fetch_one(query)
    return result[0], result[1]  # min_date, max_date
