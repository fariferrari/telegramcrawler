1.  установи все что нужно с файла "requirements.txt"
2.  чтобы настроить свой "tg_parser_project\utils\config.py" API_ID, API_HASH для входа в телеграм аккаунт, нужно для начала зайти на сайт "https://my.telegram.org/" перейти на вкладку "API development tools", заполнить всю нужную информацию и в конце получаем "App api_id:" "App api_hash:"
3.  Шаги для пересоздания chrome_profile:

    1. Удаляем старый профиль
       Открой PowerShell и введи:

       Remove-Item -Recurse -Force "E:\Telegram_crawler\chrome_profile"

       (если VSCode занят — сначала закрой его, чтобы Chrome не был в фоне)

    2. Запускаем Chrome вручную с новым профилем:

       Start-Process "chrome.exe" -ArgumentList "--user-data-dir=E:\Telegram_crawler\chrome_profile", "--profile-directory=Default"

       Это откроет чистый Chrome, привязанный к E:\Telegram_crawler\chrome_profile

    3. В новом окне:
       Перейди на https://web.telegram.org/k

       Авторизуйся через Telegram

       Перейди на https://tgstat.ru

       Авторизуйся через Telegram-кнопку (регистрация проходит через их тг бот, нужно просто нажать на кнопку "Авторизоваться")

       Убедись, что ты зашёл и сайт тебя запомнил (после того как убедился, закрой браузер)

4.  Запускаем парсер код "python main.py"
