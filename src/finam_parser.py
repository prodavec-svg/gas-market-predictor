import requests
import time
import argparse
import logging
from config import FINAM_TOKEN

def get_finam_token(api_token):
    logging.info("Авторизация на сервере Финам...")
    auth_url = "https://api.finam.ru/v1/sessions"
    try:
        response = requests.post(auth_url, json={"secret": api_token})
        response.raise_for_status()
        logging.info("Авторизация успешна. Токен сессии получен.")
        return response.json()["token"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка авторизации: {e}")
        return None

def start_parsing(token, symbol):
    quote_url = f"https://api.finam.ru/v1/instruments/{symbol}/quotes/latest"
    headers = {"Authorization": f"Bearer {token}"}

    logging.info(f"Начинаем парсить {symbol} каждую секунду. Для остановки нажми Ctrl+C")

    try:
        while True:
            response = requests.get(quote_url, headers=headers)

            if response.status_code == 429:
                logging.warning("Превышен лимит запросов! Пауза 5 секунд...")
                time.sleep(5)
                continue

            response.raise_for_status()
            data = response.json()

            quote = data.get("quote", {})
            last_price = quote.get("last", {}).get("value", "Нет данных")
            bid = quote.get("bid", {}).get("value", "-")
            ask = quote.get("ask", {}).get("value", "-")

            logging.info(f"[{symbol}] Цена: {last_price} | Bid: {bid} | Ask: {ask}")
            time.sleep(1)

    except KeyboardInterrupt:
        logging.info("Парсинг остановлен пользователем.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка соединения: {e}")

if __name__ == "__main__":
    # Настройка аргументов командной строки
    parser = argparse.ArgumentParser(description="Парсер котировок с Finam API")
    parser.add_argument(
        "--symbol",
        type=str,
        default="NGM6",
        help="Тикер инструмента для парсинга (по умолчанию NGM6)"
    )
    args = parser.parse_args()

    if not FINAM_TOKEN:
        logging.error("Невозможно запустить скрипт без API токена.")
        exit(1)

    session_token = get_finam_token(FINAM_TOKEN)

    if session_token:
        start_parsing(session_token, symbol=args.symbol)