# homework_bot
python telegram bot который обращается к API Yandex.Practicum и информирует об изменениях данных. Размещён на платформе Heroku

## Технологии

Python 3.9,
python-telegram-bot 13.7

### Запуск

- склонируйте репозиторий

```
git clone git@github.com/Anxeity/homework_bot.git
```

- в корне проекта создайте и активируйте виртуальное окружение

```
python3 -m venv venv
source venv/bin/activate
```

- установите зависимости

``` pip install -r requirements.txt ```
- создайте файл .env и добавьте в него следующие переменные:
```
PRACTICUM_TOKEN = <ваш токен на яндекс практикуме>
TELEGRAM_TOKEN = <токен вашего телеграм бота>
TELEGRAM_CHAT_ID = <id чата, в который вы хотите посылать сообщения>
```
