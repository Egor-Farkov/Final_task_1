import datetime
import os
from typing import Any
from unittest.mock import patch

import pytest
import requests

from src.utils import (
    getting_a_date_period,
    getting_exchange_rate_by_api,
    getting_stocks_price,
    main_all_info_on_cards,
    read_user_settings,
    reading_financial_transactions_from_excel,
    return_exchange_rates,
    return_of_top_transactions,
    return_welcome_text_by_date,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_getting_a_date_period() -> None:
    """
    [Тест] Функция для считывания финансовых операций из Excel выдает список словарей с транзакциями.
    """
    assert getting_a_date_period("2025-03-12 22:53:10") == (
        datetime.datetime(2025, 3, 12, 22, 53, 10),
        datetime.datetime(2025, 3, 1, 22, 53, 10),
    )


def test_reading_financial_transactions_from_excel() -> None:
    """
    [Тест] Функция для считывания финансовых операций из Excel выдает список словарей с транзакциями.
    """
    dates = (datetime.datetime(2021, 12, 27, 22, 53, 10), datetime.datetime(2021, 12, 1, 22, 53, 10))
    success_test = reading_financial_transactions_from_excel(dates, ROOT_DIR + "/data/operations.xlsx")
    assert isinstance(success_test, list)

    with pytest.raises(ValueError):
        dates = (datetime.datetime(2021, 12, 27, 22, 53, 10), datetime.datetime(2021, 12, 1, 22, 53, 10))
        reading_financial_transactions_from_excel(dates, "")

    with patch("pandas.read_excel") as read_pd:
        read_pd.return_value = "test_data"
        with pytest.raises(Exception):
            reading_financial_transactions_from_excel(dates, "")


@pytest.mark.parametrize(
    "test_datetime, result",
    [
        ("2025-03-18 08:00:23", "Доброе утро"),
        ("2025-03-16 13:00:23", "Добрый день"),
        ("2025-02-11 18:00:23", "Добрый вечер"),
        ("2023-10-12 23:00:23", "Доброй ночи"),
    ],
)
def test_return_welcome_text_by_date(test_datetime: str, result: str) -> None:
    """
    [Тест] Функция возврата строки приветствия по дате форматом YYYY-MM-DD HH:MM:SS.
    """
    assert return_welcome_text_by_date(test_datetime) == result


def test_main_all_info_on_cards(excel_data: list[dict]) -> None:
    """
    [Тест] Функция вывода всей информации по картам.
    """
    data = main_all_info_on_cards(excel_data)
    assert data == [{"cashback": 0.0, "last_digits": "7197", "total_spent": 8023.92}]

    with pytest.raises(Exception):
        main_all_info_on_cards([{}])


def test_return_of_top_transactions(excel_data: list[dict]) -> None:
    """
    [Тест] Функция возврата ТОП 5 транзакций.
    """
    data = return_of_top_transactions(excel_data)
    assert data == [
        {
            "amount": 115909.42,
            "category": "Переводы",
            "date": "24.01.2018",
            "description": "Перевод Кредитная карта. ТП 10.2 RUR",
        },
        {"amount": 9700.0, "category": "Пополнения", "date": "25.01.2018", "description": "Перевод с карты"},
        {"amount": 5748.0, "category": "Авиабилеты", "date": "25.01.2018", "description": "Aviacassa"},
        {"amount": 840.3, "category": "Ж/д билеты", "date": "24.01.2018", "description": "РЖД"},
        {"amount": 376.0, "category": "Транспорт", "date": "25.01.2018", "description": "Яндекс Такси"},
    ]


@patch("requests.get")
def test_getting_exchange_rate_by_api(requests_mock: Any) -> None:
    """
    [Тест] Функция получения курса валюты по API
    """
    requests_mock.return_value.status_code = 200
    requests_mock.return_value.json.return_value = {"rates": {"RUB": 1.887787}}
    data = getting_exchange_rate_by_api("USD")
    assert data == 1.887787

    requests_mock.return_value.status_code = 500
    data = getting_exchange_rate_by_api("USD")
    assert data == 0

    requests_mock.side_effect = requests.exceptions.ReadTimeout
    with pytest.raises(requests.exceptions.ReadTimeout):
        getting_exchange_rate_by_api("USD")


@patch("requests.get")
def test_getting_stocks_price(requests_mock: Any) -> None:
    """
    [Тест] Функция получения стоимости акций.
    """
    requests_mock.return_value.status_code = 200
    requests_mock.return_value.json.return_value = {"Global Quote": {"05. price": 32.223}}
    data = getting_stocks_price("USD")
    assert data == 32.223

    requests_mock.return_value.status_code = 200
    requests_mock.return_value.json.return_value = {"Global Quotes": {"05. price": 32.223}}
    with pytest.raises(Exception):
        getting_stocks_price("USD")

    requests_mock.return_value.status_code = 500
    data = getting_stocks_price("USD")
    assert data == 0


@patch("requests.get")
def test_return_exchange_rates(requests_mock: Any) -> None:
    """
    [Тест] Функция возвращает курс валют.
    """
    requests_mock.return_value.status_code = 200
    requests_mock.return_value.json.return_value = {"rates": {"RUB": 32.223}}

    data = return_exchange_rates()
    assert data == [{"currency": "USD", "rate": 32.22}, {"currency": "EUR", "rate": 32.22}]


@patch("requests.get")
def test_get_stocks_price(requests_mock: Any) -> None:
    """
    [Тест] Функция возвращает стоимость акций.
    """
    requests_mock.return_value.status_code = 200
    requests_mock.return_value.json.return_value = {"Global Quote": {"05. price": 322.223}}
    data = getting_stocks_price("USD")
    assert data == 322.223


def test_read_user_settings() -> None:
    """
    [Тест] Функция чтения пользовательских настроек.
    """
    data = read_user_settings()
    assert data == {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}

    with patch("builtins.open") as f_open:
        f_open("fake_file")
        with pytest.raises(Exception):
            read_user_settings()
