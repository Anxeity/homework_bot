import logging
import os
import sys
import time

import requests
import telegram
import exceptions
from dotenv import load_dotenv
from http import HTTPStatus


load_dotenv()


PRACTICUM_TOKEN = os.getenv('YA_TOKEN')
TELEGRAM_TOKEN = os.getenv('TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# Добавляем файловый лог
fileHandler = logging.FileHandler('homework.log')
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)
# Добавляем вывод лога в консоль
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


def send_message(bot, message):
    """Функция отправляет сообщения в Телеграм."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except exceptions.TrySendMessageError as error:
        logger.error(
            f'Ошибка при отправке сообщения: {error}')
    else:
        logger.info('Сообщение отправлено')


def get_api_answer(current_timestamp):
    """Функция отправляет запрос к апи."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except Exception as error:
        message = f'Запрос не отправлен: {error}'
        logger.error(message)
        raise Exception(message)
    if homework_statuses.status_code != HTTPStatus.OK:
        messagest = 'Статус код не 200'
        logger.error(messagest)
        raise exceptions.NegativeApiStatus(messagest)
    return homework_statuses.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    try:
        homeworks_list = response['homeworks']
    except KeyError:
        message = 'API отсутсвуют ключ homeworks'
        logger.error(message)
        raise KeyError(message)
    if not isinstance(homeworks_list, list):
        message = 'Перечень домашки не является списком'
        logger.error(message)
        raise exceptions.HomeWorkIsNotList(message)
    homework = homeworks_list[0]
    return homework


def parse_status(homework):
    """Извлекает статус домашней работы."""
    if 'homework_name' not in homework:
        message = 'Нет ключа homework_name в API'
        logger.error(message)
        raise KeyError(message)
    if 'status' not in homework:
        message = 'Нет ключа "status" в API'
        logger.error(message)
        raise exceptions.HomewokrStatusError(message)
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise Exception(f'Неизвестный статус работы: {homework_status}')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if (
        PRACTICUM_TOKEN is None
        or TELEGRAM_TOKEN is None
        or TELEGRAM_CHAT_ID is None
    ):
        logger.critical('токены отсутствуют!')
        return False
    return True


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        raise KeyError('Отсутствуют обязательные переменные окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            print(message)
            send_message(bot, message)
            current_timestamp = response.get('current_date')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
