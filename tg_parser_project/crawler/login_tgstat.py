from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def login_to_tgstat():
    options = Options()
    options.add_argument("user-data-dir=E:\\Telegram_crawler\\chrome_profile")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://kaz.tgstat.com/ratings/chats/public?sort=members")

        login_buttons = driver.find_elements(By.XPATH, "//a[@data-src='/login']")
        if login_buttons:
            login_buttons[0].click()

            telegram_btn = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "auth-btn"))
            )
            tg_link = telegram_btn.get_attribute("href")

            web_link = tg_link.replace("https://t.me", "https://web.telegram.org/k")
            driver.get(web_link)

            authorize_btn = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[.//span[contains(text(), 'Авторизоваться')]]")
                )
            )
            authorize_btn.click()

            time.sleep(5)
            driver.get("https://kaz.tgstat.com/ratings/chats/public?sort=members")
            print("Авторизация завершена")

        else:
            print("Уже авторизован в TGStat")

        return driver

    except Exception as e:
        print(f"Ошибка входа: {e}")
        driver.quit()
        return None
