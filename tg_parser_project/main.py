# main.py

import asyncio
import os
import csv
from parser.telegram_downloader import collect_messages_from_chat

CSV_PATH = "data/Tg_links_20250619_180322.csv"


def read_links_from_csv(path):
    links = []
    if not os.path.exists(path):
        return links

    with open(path, encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            link = row.get("Telegram Chat Link")
            if link:
                links.append(link.strip())
    return links


async def run():
    links = read_links_from_csv(CSV_PATH)
    if links:
        print(f"Найдено {len(links)} ссылок в CSV. Начинаем парсинг...")
        for link in links:
            print(f"\n▶ Парсим: {link}")
            await collect_messages_from_chat(link)
    else:
        chat = input("Введите ссылку на чат: ")
        await collect_messages_from_chat(chat)


if __name__ == "__main__":
    asyncio.run(run())
