import os
import logging
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Настраиваем формат логов (время - уровень - сообщение)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

FINAM_TOKEN = os.getenv("FINAM_API_TOKEN")

if not FINAM_TOKEN:
    logging.warning("Токен Финам не найден! Проверь файл .env")