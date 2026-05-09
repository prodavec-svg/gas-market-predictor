import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout


def create_sequences(data, seq_length):
    """
    Разбивает данные на последовательности (X) и целевые значения (y).
    Например, используем 60 прошлых шагов, чтобы предсказать 1 следующий.
    """
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:(i + seq_length), 0])
        y.append(data[i + seq_length, 0])
    return np.array(X), np.array(y)


def run_lstm_prediction(csv_file):
    print(f"Загрузка данных из {csv_file}...")

    # 1. Загрузка данных
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print("Файл не найден. Убедись, что указал правильное имя файла.")
        return

    # Нам интересна только цена закрытия
    data = df.filter(['Close']).values

    # 2. Нормализация данных (масштабируем от 0 до 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # 3. Подготовка тренировочных и тестовых данных
    seq_length = 60  # Размер "окна" - смотрим на 60 шагов назад

    # Разделяем на train (80%) и test (20%)
    training_data_len = int(np.ceil(len(scaled_data) * .8))
    train_data = scaled_data[0:int(training_data_len), :]

    x_train, y_train = create_sequences(train_data, seq_length)

    # Keras ожидает формат данных [samples, time steps, features]
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    # 4. Создание архитектуры модели LSTM
    print("Создание и компиляция модели...")
    model = Sequential()
    # Первый слой LSTM
    model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(Dropout(0.2))  # Защита от переобучения

    # Второй слой LSTM
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))

    # Полносвязные слои
    model.add(Dense(25))
    model.add(Dense(1))  # Выходной слой - одно предсказанное значение

    # Компиляция
    model.compile(optimizer='adam', loss='mean_squared_error')

    # 5. Обучение модели
    print("Старт обучения (может занять пару минут)...")
    model.fit(x_train, y_train, batch_size=32, epochs=10)  # 10 эпох для скорости, для точности нужно больше

    # 6. Подготовка тестовых данных и предсказание
    test_data = scaled_data[training_data_len - seq_length:, :]
    x_test, y_test_actual = create_sequences(test_data, seq_length)
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    # Получаем предсказания модели
    predictions = model.predict(x_test)

    # Де-нормализуем предсказания обратно в реальные цены
    predictions = scaler.inverse_transform(predictions)

    # 7. Визуализация результата
    train = df[:training_data_len].copy()
    valid = df[training_data_len:].copy()

    # Убедимся, что длины совпадают (может быть небольшая разница из-за seq_length)
    valid = valid.iloc[:len(predictions)]
    valid.loc[:, 'Predictions'] = predictions

    plt.figure(figsize=(16, 8))
    plt.title('Модель LSTM для фьючерсов на газ')
    plt.xlabel('Индекс (время)', fontsize=12)
    plt.ylabel('Цена закрытия', fontsize=12)

    plt.plot(train['Close'], color='blue', label='Обучающая выборка')
    plt.plot(valid.index, valid['Close'], color='green', label='Реальная цена (тест)')
    plt.plot(valid.index, valid['Predictions'], color='red', label='Предсказание модели', linestyle='dashed')

    plt.legend(loc='lower right')
    plt.show()


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="LSTM модель для предсказания цены")
    parser.add_argument("--file", type=str, required=True, help="Имя CSV файла (должен лежать в папке data/)")

    args = parser.parse_args()

    filepath = os.path.join("data", args.file)

    if not os.path.exists(filepath):
        print(f"Ошибка: Файл {filepath} не найден. Сначала скачай данные через moex_client.py")
    else:
        run_lstm_prediction(filepath)