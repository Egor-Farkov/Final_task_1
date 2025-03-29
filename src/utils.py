import json
import logging
import os
from datetime import datetime
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

from config import ROOT_DIR

load_dotenv()


utils_logger = logging.getLogger(__name__)
utils_logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(ROOT_DIR + "/logs/logging_utils.log", mode="w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(module)s %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
utils_logger.addHandler(file_handler)

API_KEY = os.getenv("API_KEY")
API_KEY_STOCKS = os.getenv("API_KEY_STOCKS")


def getting_a_date_period(date: str) -> tuple[datetime, datetime]:
    """
    Функция получает период дат с начала месяца до указанной даты.
    :param date: Строка даты
    :return: Тип datetime
    """
    format_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    utils_logger.info("Кортеж с периодом дат успешно создан")
    return format_date, format_date.replace(day=1)


def reading_financial_transactions_from_excel(
    period_datetime: tuple[datetime, datetime], filename: str | None = ROOT_DIR + "/data/operations.xlsx"
) -> list[dict[Any, Any]]:
    """
    Функция считывает финансовые операций из Excel и выдает список словарей с транзакциями.
    :param filename: Путь к файлу Excel.
    :param period_datetime: Лист для сортировки с периодом начала и указанной датой.
    :return: Список словарей с транзакциями.
    """
    if filename:
        try:
            data_excel = pd.read_excel(filename)
            end_date, start_date = period_datetime
            group_data = data_excel.to_dict("records")
            filtered_data = [
                data
                for data in list(group_data)
                if datetime.strptime(data["Дата операции"], "%d.%m.%Y %H:%M:%S") >= start_date
                and datetime.strptime(data["Дата операции"], "%d.%m.%Y %H:%M:%S") <= end_date
            ]
            utils_logger.info("Данные по файлу транзакций отфильтрованы по дате и готовы к работе")
            return list(filtered_data)
        except Exception:
            utils_logger.error("Произошла ошибка в чтении файла и/или в преобразовании ячейки в формат даты")
            raise Exception("Произошла ошибка в чтении файла и/или в преобразовании ячейки в формат даты")
    else:
        utils_logger.error("filename не указан и равен None")
        raise ValueError("filename не указан и равен None")


def return_welcome_text_by_date(date: str) -> str:
    """
    Функция возврата строки с приветствием по дате.
    :param date: Дата формата YYYY-MM-DD HH:MM:SS.
    :return: Приветствие от переданного времени.
    """
    input_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    hour = input_datetime.hour
    if 4 <= hour <= 11:
        welcome = "Доброе утро"
    elif 12 <= hour < 17:
        welcome = "Добрый день"
    elif 17 <= hour < 22:
        welcome = "Добрый вечер"
    else:
        welcome = "Доброй ночи"
    utils_logger.info("Успешно определено время, приветствие сформировано")
    return welcome


def main_all_info_on_cards(transactions: list[dict]) -> list[dict]:
    """
    Функция вывода всей информации по картам.
    :param transactions: Входные данные с транзакциями.
    :return: Информация по картам.
    """
    try:
        df = pd.DataFrame(transactions)
        cards = []

        add_group_data = df.groupby("Номер карты").agg({"Сумма операции с округлением": "sum", "Кэшбэк": "sum"})
        for card_num, row in add_group_data.iterrows():
            info_card = {
                "last_digits": str(card_num)[-4:],
                "total_spent": float(row["Сумма операции с округлением"]),
                "cashback": float(row["Кэшбэк"]),
            }
            cards.append(info_card)
        utils_logger.info("Список карт успешно сформирован в лист")
        return cards
    except Exception:
        utils_logger.error("Empty DataFrame - данные пусты, поменяйте дату")
        raise ValueError("Empty DataFrame - данные пусты, поменяйте дату")


def return_of_top_transactions(transactions: list[dict]) -> list[dict]:
    """
    Функция возврата пяти топовых транзакций.
    :param transactions: Список транзакций.
    :return: Список пяти топовых транзакций по сумме.
    """
    top_transaction = []
    df = pd.DataFrame(transactions)
    top_data = df.sort_values(by="Сумма операции с округлением", ascending=False).head(5)
    for data, row in top_data.iterrows():
        top_transaction.append(
            {
                "date": row["Дата платежа"],
                "amount": float(row["Сумма операции с округлением"]),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )
    utils_logger.info("Список пяти топовых транзакций сформирован")
    return top_transaction


def getting_exchange_rate_by_api(currency: str) -> float:
    """
    Функция получения курса валюты по API
    :param currency: Название валюты
    :return: Результат курса валюты
    """
    date = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.apilayer.com/exchangerates_data/{date}"
    params = {"base": currency, "symbols": "RUB"}
    headers = {"apikey": API_KEY}
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            rates = data["rates"]["RUB"]
            utils_logger.info("Данные API успешно запрошены")
            return float(rates)
    except requests.exceptions.ReadTimeout:
        utils_logger.error("Превышено время соединения с сервером API")
        raise requests.exceptions.ReadTimeout("Превышено время соединения с сервером API")
    utils_logger.warning("Возвращаем '0' что-то с запросом API пошло не так")
    return 0


def getting_stocks_price(stocks: str) -> float:
    """
    Функция получения стоимости акций.
    :param stocks: Название акции.
    :return: Стоимость.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": stocks,
        "apikey": API_KEY_STOCKS,
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            utils_logger.info("Данные API успешно запрошены")
            return float(data["Global Quote"]["05. price"])
    except Exception:
        utils_logger.error("Произошла ошибка")
        raise Exception("Произошла ошибка")
    utils_logger.warning("Возвращаем '0' что-то с запросом API пошло не так")
    return 0


def return_exchange_rates() -> list[dict]:
    """
    Функция возвращает курс валют.
    :return: Курсы валют.
    """
    user_settings = read_user_settings()
    user_currencies = user_settings["user_currencies"]
    data_rates = []
    for currency in user_currencies:
        rates = getting_exchange_rate_by_api(currency)
        data_rates.append({"currency": currency, "rate": round(rates, 2)})
    utils_logger.info("Курс валют успешно возвращен")
    return data_rates


def get_stocks_price() -> list[dict]:
    """
    Функция возвращает стоимость акций.
    :return: Список стоимости акций.
    """
    user_settings = read_user_settings()
    all_stocks = user_settings["user_stocks"]
    data_stocks = []
    for stocks in all_stocks:
        stock = getting_stocks_price(stocks)
        data_stocks.append({"stock": stocks, "price": round(stock, 2)})
    utils_logger.info("Стоимости акций успешно возвращены")
    return data_stocks


def read_user_settings() -> dict:
    """
    Функция чтения пользовательских настроек.
    :return: Json объект Python.
    """
    try:
        with open(ROOT_DIR + "/user_settings.json") as f:
            data = dict(json.load(f))
            utils_logger.info("Файл настроек успешно считан")
            return data
    except Exception:
        utils_logger.error("Ошибка чтения структуры json файла или файл отсутствует")
        raise Exception("Ошибка чтения структуры json файла или файл отсутствует")
