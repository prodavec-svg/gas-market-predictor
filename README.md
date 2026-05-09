
# Программный комплекс для сбора, обработки и прогнозирования котировок фьючерсов на природный газ (NG) с использованием API Московской Биржи (MOEX) и Финам.

## Функциональные возможности

- **Сбор исторических данных (MOEX):** Выгрузка свечного графика в формате CSV.
- **Мониторинг в реальном времени (Финам):** Парсинг потоковых данных (bid/ask/last) с контролем частоты запросов.
- **Оценка сетевых задержек:** Замер времени отклика серверов биржи.
- **Прогнозирование:** Обучение и запуск нейронной сети архитектуры LSTM.

## Технологический стек

- Python 3.10
- Библиотеки обработки данных: Pandas, NumPy, Scikit-learn
- Машинное обучение: TensorFlow (Keras)
- Инструментарий API: Requests, Apimoex

## Установка и настройка

1. Клонирование репозитория:  
   ```
      git clone https://github.com/prodavec-svg/gas-market-predictor.git
      cd gas-market-predictor
   ```

2. Настройка окружения Conda:
    ```
   conda create -n gas_env python=3.10 -y
   conda activate gas_env
   pip install -r requirements.txt
    ```

3. Конфигурация:
   Создать файл .env в корневой директории.
   Добавить параметр: 
    ```
   FINAM_API_TOKEN=<ваш_токен>
    ```

## Инструкции по эксплуатации

### 1. Модуль MOEX (moex_client.py)

- Получение списка доступных тикеров:  
```python src/moex_client.py --mode list```
  

- Замер задержки API(для примера TICKER=NGM6, INT=5):  
  ```python src/moex_client.py --mode ping --ticker <TICKER> --ping_count <INT>```

- Выгрузка исторических данных:  
  ```python src/moex_client.py --mode download --ticker <TICKER> --start <YYYY-MM-DD> --end <YYYY-MM-DD>```

### 2. Модуль прогнозирования (ml_predict.py)

- Обучение модели на основе CSV-файла:  
  ```python src/ml_predict.py --file <filename.csv>```

### 3. Модуль реального времени (finam_parser.py)

- Запуск потокового парсинга:  
  ```python src/finam_parser.py --symbol <SYMBOL>```