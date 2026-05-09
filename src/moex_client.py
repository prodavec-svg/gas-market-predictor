import os
import time
import argparse
import logging
import requests
import pandas as pd
import apimoex
from datetime import datetime, timedelta

# Настраиваем логирование для этого модуля
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_ng_tickers(session):
    """Получает список всех фьючерсов на газ"""
    logging.info("Запрашиваем доступные фьючерсы на газ (NG)...")
    futures = apimoex.get_board_securities(session, board='RFUD', engine='futures', market='forts')
    df = pd.DataFrame(futures)
    ng_tickers = df[df['SECID'].str.startswith('NG')]

    print("\nДоступные фьючерсы на газ:")
    print(ng_tickers[['SECID', 'SHORTNAME']].to_string(index=False))
    print("-" * 30)


def evaluate_ping(session, ticker, num_requests=5):
    """Оценивает задержку API MOEX"""
    logging.info(f"Оценка времени отклика MOEX API для тикера {ticker}...")
    url = f"https://iss.moex.com/iss/engines/futures/markets/forts/boards/RFUD/securities/{ticker}/candles.json"
    params = {"from": "2026-05-05", "till": "2026-05-06", "interval": 10}

    total_server_time = 0
    total_full_time = 0

    for i in range(1, num_requests + 1):
        try:
            start_time = time.time()
            response = session.get(url, params=params)
            response.raise_for_status()

            server_time = response.elapsed.total_seconds()
            full_time = time.time() - start_time

            total_server_time += server_time
            total_full_time += full_time

            logging.info(f"Запрос {i}/{num_requests}: Сервер = {server_time:.4f}с | Полностью = {full_time:.4f}с")
            time.sleep(0.5)
        except requests.exceptions.RequestException as e:
            logging.error(f"Ошибка запроса {i}: {e}")

    if num_requests > 0:
        logging.info(
            f"СРЕДНЕЕ: API Latency = {total_server_time / num_requests:.4f}с | Total = {total_full_time / num_requests:.4f}с")


def fetch_candles(session, ticker, start, end):
    """Скачивает свечи и сохраняет в папку data/"""
    logging.info(f"Выгрузка данных {ticker} с {start} по {end}...")

    data = apimoex.get_board_candles(
        session, security=ticker, board='RFUD', engine='futures', market='forts',
        start=start, end=end, interval=1
    )

    if not data:
        logging.warning("Данные не найдены. Проверьте даты или тикер.")
        return

    df = pd.DataFrame(data)
    df = df[['begin', 'open', 'close', 'high', 'low', 'volume']]
    df.columns = ['Datetime', 'Open', 'Close', 'High', 'Low', 'Volume']

    # Убедимся, что папка data существует
    os.makedirs("data", exist_ok=True)

    filename = f"data/moex_{ticker}_{start}_to_{end}.csv"
    df.to_csv(filename, index=False)

    logging.info(f"Успех! Скачано строк: {len(df)}. Файл сохранен: {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Клиент данных MOEX")
    parser.add_argument("--mode", choices=['list', 'ping', 'download'], required=True,
                        help="Режим работы: list (показать тикеры), ping (замерить задержку), download (скачать свечи)")
    parser.add_argument("--ticker", type=str, default="NGM6", help="Тикер (например, NGM6)")
    parser.add_argument("--start", type=str, default=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                        help="Дата начала (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default=datetime.now().strftime("%Y-%m-%d"),
                        help="Дата окончания (YYYY-MM-DD)")
    parser.add_argument("--ping_count", type=int, default=5, help="Количество запросов для пинга")

    args = parser.parse_args()

    with requests.Session() as session:
        if args.mode == 'list':
            get_ng_tickers(session)
        elif args.mode == 'ping':
            evaluate_ping(session, ticker=args.ticker, num_requests=args.ping_count)
        elif args.mode == 'download':
            fetch_candles(session, ticker=args.ticker, start=args.start, end=args.end)