import os
import json
import asyncio
from telethon import TelegramClient
from telethon.tl.types import (
    MessageService,
    User,
    MessageMediaPhoto,
    MessageMediaDocument,
    DocumentAttributeVideo,
    PeerUser,
    MessageEntityMention,
    MessageEntityTextUrl,
)
from utils.config import API_ID, API_HASH, SESSION_NAME
from utils.db import insert_messages
from telethon.errors import RpcCallFailError
from datetime import datetime

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


async def is_human(user):
    return isinstance(user, User) and not user.bot and not user.deleted


def get_media_type(message):
    if isinstance(message.media, MessageMediaPhoto):
        return "photo"
    if isinstance(message.media, MessageMediaDocument):
        if message.file and message.file.mime_type == "video/mp4":
            for attr in message.document.attributes:
                if isinstance(attr, DocumentAttributeVideo):
                    return "video"
            return "gif"
        return "file"
    if message.sticker:
        return "sticker"
    if message.voice:
        return "voice"
    if message.audio:
        return "audio"
    return "text" if message.text else "none"


def extract_mentions(message):
    mentions = []
    if message.entities:
        for entity in message.entities:
            if isinstance(entity, MessageEntityMention) or isinstance(
                entity, MessageEntityTextUrl
            ):
                mention = message.text[entity.offset : entity.offset + entity.length]
                mentions.append(mention)
    return mentions


def has_links(message):
    return "http://" in (message.text or "") or "https://" in (message.text or "")


async def collect_messages_from_chat(chat_link: str, save_to_json=True):
    await client.start()
    try:
        if chat_link.startswith("https://t.me/"):
            entity = await client.get_entity(chat_link)
        elif chat_link.startswith("https://web.telegram.org/k/#-"):
            chat_id = int(chat_link.split("#-")[-1])
            entity = await client.get_input_entity(chat_id)
        elif chat_link.startswith("@") or chat_link.isalnum():
            entity = await client.get_entity(chat_link)
        else:
            raise ValueError("Неизвестный формат ссылки")
    except Exception as e:
        print(f"Ошибка при получении entity: {e}")
        return []

    messages = []
    print(f"Скачиваем из: {chat_link}")

    max_retries = 3
    for attempt in range(max_retries):
        try:
            async for msg in client.iter_messages(entity, reverse=True):
                if isinstance(msg, MessageService):
                    continue

                try:
                    sender = await msg.get_sender()

                    if sender is None:
                        continue

                    if not await is_human(sender):
                        continue

                    msg_data = {
                        "msg_id": msg.id,
                        "chat_id": entity.id,
                        "text": msg.text or f"[{get_media_type(msg)}]",
                        "media_type": get_media_type(msg),
                        "reply_to_msg_id": msg.reply_to_msg_id,
                        "fwd_from_user_id": msg.fwd_from.from_id.user_id
                        if msg.fwd_from and isinstance(msg.fwd_from.from_id, PeerUser)
                        else None,
                        "views": msg.views,
                        "reactions": [
                            r.reaction.emoticon
                            for r in (msg.reactions.results if msg.reactions else [])
                        ],
                        "mentions": extract_mentions(msg),
                        "has_links": has_links(msg),
                        "date": str(msg.date),
                        "user": {
                            "user_id": sender.id,
                            "username": sender.username,
                            "first_name": sender.first_name,
                            "last_name": sender.last_name,
                            "phone": getattr(sender, "phone", None),
                            "lang_code": getattr(sender, "lang_code", None),
                            "is_verified": getattr(sender, "verified", False),
                            "is_scam": getattr(sender, "scam", False),
                            "status": str(sender.status)
                            if hasattr(sender, "status")
                            else None,
                        },
                    }

                    messages.append(msg_data)

                except Exception as e:
                    print(f"Ошибка при разборе сообщения (msg_id={msg.id}): {e}")
                    continue
            break
        except RpcCallFailError as e:
            print(f"Попытка {attempt + 1} неудачна: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(10)
            else:
                print("Повторные попытки не помогли.")
                return []

    print(f"Собрано: {len(messages)} сообщений")

    if save_to_json:
        os.makedirs("data/messages", exist_ok=True)
        chat_title = (
            getattr(entity, "username", None)
            or getattr(entity, "title", None)
            or f"chat_{entity.id}"
        )
        chat_title = chat_title.replace(" ", "_").replace("@", "").lower()
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_name = f"data/messages/{chat_title}_{entity.id}_{date_str}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        print(f"Сохранено в {file_name}")

    insert_messages(entity.id, messages)
    print(f"Сохранено в PostgreSQL ({entity.id}, {len(messages)} сообщений)")

    return messages
