import json
import logging
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
file_json = os.path.join(project_root, "user_settings.json")

current_dir = os.path.dirname(os.path.abspath(__file__))

rel_file_path = os.path.join(current_dir, "../logs/utils.log")
abs_file_path = os.path.abspath(rel_file_path)

logger = logging.getLogger("utils")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(abs_file_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

load_dotenv()
for_currency = os.getenv("API_KEY_FOR_CURRENCY")
for_share = os.getenv("API_KEY_FOR_STOCK")


def get_data_from_excel(path_to_the_file: str) -> pd.DataFrame | list:
    """Функция, которая возвращает данные о финансовых транзакциях из файла excel"""
    try:
        pd.read_excel(path_to_the_file)

    except ValueError as ex:
        logger.error(f"Произошла ошибка {ex}")

        return []

    except FileNotFoundError as ex:
        logger.error(f"Произошла ошибка {ex}")

        return []

    else:
        operations = pd.read_excel(path_to_the_file)
        logger.info("Успешное выполнение")
        return operations.to_dict(orient="records")


def filter_date_operations(operations: pd.DataFrame, date: str) -> list:
    """Возвращает операции за текущий месяц"""
    first_day_moth = datetime.strptime(date, "%Y-%m-%d %H:%M:%S").replace(day=1, hour=00, minute=00, second=00)
    operations["Дата операции"] = pd.to_datetime(operations["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    return operations[
        (operations["Дата операции"] >= first_day_moth)
        & (operations["Дата операции"] <= datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
    ]


def greeting_user() -> str:
    """Возвращает приветствие в зависимости от времени суток"""
    logger.info("Приветствуем пользователя")
    current_hour = datetime.now().hour
    if current_hour < 6:
        return "Доброй ночи"
    elif current_hour < 12:
        return "Доброе утро"
    elif current_hour < 18:
        return "Добрый день"
    else:
        return "Добрый вечер"


def operations_cards(operations: pd.DataFrame) -> list:
    """Возвращает данные по каждой карте"""
    grouped_operations = operations.groupby("Номер карты")["Сумма операции с округлением"].sum().reset_index()
    grouped_operations["Cashback"] = (grouped_operations["Сумма операции с округлением"] // 100).astype(int)
    grouped_operations["LastFourDigits"] = grouped_operations["Номер карты"].astype(str).str[-4:]
    result = grouped_operations[["LastFourDigits", "Сумма операции с округлением", "Cashback"]]
    result.columns = ["last_digits", "total_spent", "cashback"]

    return result.to_dict(orient="records")


def top_five_transactions(operations: pd.DataFrame) -> list:
    """Возвращает топ-5 транзакций по сумме платежа"""
    result = []
    top_transactions = operations.nlargest(5, "Сумма операции с округлением")
    for transaction in top_transactions.to_dict(orient="records"):
        result.append(
            {
                "date": transaction["Дата операции"],
                "amount": transaction["Сумма операции с округлением"],
                "category": transaction["Категория"],
                "description": transaction["Описание"],
            }
        )
    return result


import requests  # noqa


def currency_rates():
    # Пример запроса к API (замени на свой реальный URL)
    response = requests.get(f"https://financialmodelingprep.com/api/v3/search?query=AA&apikey={for_currency}")

    # Проверка, что статус ответа 200 (OK)
    if response.status_code != 200:
        print(f"Ошибка API: {response.status_code}")
        return []  # Возвращаем пустой список, если ошибка с запросом

    try:
        # Получаем JSON-ответ
        data = response.json()
        # Печатаем ответ, чтобы увидеть его структуру
        print(data)

        # Используем .get() для безопасного доступа к 'data'
        currencies = data.get("data", {})  # Возвращаем пустой словарь, если ключ 'data' отсутствует
        result_currencies = []

        for currency, value in currencies.items():
            result_currencies.append({"currency": currency, "rate": round(value["value"], 2)})

        return result_currencies

    except Exception as e:
        print(f"Ошибка при обработке данных: {e}")
        return []  # Возвращаем пустой список при ошибке


def stock_prices() -> list:
    """Возвращает стоимость акций из S&P 500"""
    logger.info("Поиск основных акций из S&P500")
    url = f"https://api.marketstack.com/v1/eod/latest?access_key={for_share}"
    result = []

    # Открытие и чтение JSON с пользовательскими акциями
    with open(file_json, encoding="utf-8") as file:
        user_shares = json.load(file)
        user_share = ",".join(user_shares["user_stocks"])
        querystring = {"symbols": user_share}

        response = requests.get(url, params=querystring)

        # Проверка статуса ответа
        if response.status_code != 200:
            print(f"Ошибка API: {response.status_code}")
            return []  # Возвращаем пустой список при ошибке запроса

        try:
            response_data = response.json()  # Пытаемся получить данные в формате JSON

            # Проверка наличия ключа 'data' в ответе
            if "data" in response_data:
                for data in response_data["data"]:
                    result.append({"stock": data["symbol"], "price": data["close"]})
            else:
                print("Ответ не содержит данных по акциям.")
                return []  # Возвращаем пустой список, если данных нет

        except Exception as e:
            print(f"Ошибка при обработке данных: {e}")
            return []  # Возвращаем пустой список при ошибке

    return result


def convert_timestamps_to_strings(dataframe):
    """Преобразует все столбцы с типом 'datetime64[ns]' в строки."""
    for col in dataframe.select_dtypes(include=["datetime64[ns]"]).columns:
        dataframe[col] = dataframe[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    return dataframe
