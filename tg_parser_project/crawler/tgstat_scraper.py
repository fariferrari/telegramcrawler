from crawler.login_tgstat import login_to_tgstat
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import csv
import os
import time


def save_to_csv(rows):
    os.makedirs("data", exist_ok=True)
    file_path = f"data/Tg_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["TGStat Chat URL", "Telegram Chat Link"])
        writer.writerows(rows)
    print(f"Сохранено в {file_path}")


def scroll_to_bottom(browser, max_scrolls=30):
    last_height = browser.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        browser.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(1.5)
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def get_chat_links(browser):
    print("Ожидаем загрузку карточек чатов...")
    WebDriverWait(browser, 30).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".peer-item-row"))
    )

    scroll_to_bottom(browser)

    elems = browser.find_elements(By.CSS_SELECTOR, ".peer-item-row a")
    links = []
    seen = set()

    for el in elems:
        href = el.get_attribute("href")
        if href and "/chat/@" in href and href not in seen:
            links.append(href)
            seen.add(href)

    print(f"Найдено {len(links)} ссылок на TGStat-страницы чатов")
    return links


def extract_telegram_links(browser, url):
    browser.execute_script("window.open('');")
    browser.switch_to.window(browser.window_handles[-1])
    browser.get(url)

    link = None
    try:
        WebDriverWait(browser, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".text-center.text-sm-left a.btn.btn-outline-info")
            )
        )

        a_tag = browser.find_element(
            By.CSS_SELECTOR, ".text-center.text-sm-left a.btn.btn-outline-info"
        )

        href = a_tag.get_attribute("href")
        text = a_tag.text.strip()

        if href.startswith("https://t.me/") and text.startswith("@"):
            link = href

    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")

    browser.close()
    browser.switch_to.window(browser.window_handles[0])
    return [link] if link else []


def collect_all(browser):
    results = []
    tgstat_links = get_chat_links(browser)

    if not tgstat_links:
        print("Не найдено ни одной карточки чата.")
        return results

    for link in tgstat_links:
        try:
            tg_links = extract_telegram_links(browser, link)
            results.append((link, ", ".join(tg_links)))
            print(f"{link} → {len(tg_links)} ссылок")
        except Exception as e:
            print(f"Ошибка при обработке {link}: {e}")
    return results


if __name__ == "__main__":
    browser = login_to_tgstat()
    if browser:
        try:
            print("Логин успешен, открываем рейтинг чатов...")
            browser.get("https://kaz.tgstat.com/ratings/chats/public?sort=members")
            all_data = collect_all(browser)
            if all_data:
                save_to_csv(all_data)
            else:
                print("Нет данных для сохранения.")
        finally:
            browser.quit()
