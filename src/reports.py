import datetime
import json
import logging
from datetime import timedelta
from functools import wraps
from typing import Any, Optional

import pandas as pd

from config import ROOT_DIR

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(ROOT_DIR + "/logs/reports.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(module)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def log(filename: Any = None) -> Any:
    """Декоратор, который логирует ход выполнения функции, ее результаты и возникшие ошибки"""

    def my_decorator(func: Any) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            message_in_log: str = ""
            try:
                data = func(*args, **kwargs)
                message_in_log = json.dumps(list(data.to_dict("records")))
            except Exception as e:
                message_in_log = f"{func.__name__} Ошибка {type(e).__name__} {args} {kwargs}"
            finally:
                if filename:
                    with open(ROOT_DIR + f"/logs/{filename}", "a") as file:
                        file.write(str(message_in_log) + "\n")
                else:
                    print(str(message_in_log))

            return message_in_log

        return wrapper

    return my_decorator


def reading_financial_from_reports_excel(filename: str | None = ROOT_DIR + "/data/operations.xlsx") -> pd.DataFrame:
    """
    Функция считывает финансовые операций из Excel и выдает список словарей с транзакциями.
    :param filename: Путь к файлу Excel.
    :return: DataFrame класса pandas.
    """
    if filename:
        try:
            data_excel = pd.read_excel(filename)
            logger.info("Данные считаны успешно")
            return data_excel
        except Exception as e:
            logger.error("Произошла ошибка в чтении файла")
            raise e
    else:
        logger.error("filename не указан и равен None")
        raise ValueError("filename не указан и равен None")


@log("test.log")
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Функция затрат по категории возвращающая в формате DataFrame"""
    if not date:
        end_date = datetime.datetime.now()
    else:
        end_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    start_date = end_date - timedelta(days=90)

    dict_data = transactions.to_dict("records")
    all_buys = []
    for s_data in dict_data:
        valid_start_day = datetime.datetime.strptime(s_data["Дата операции"], "%d.%m.%Y %H:%M:%S") >= start_date
        valid_end_day = datetime.datetime.strptime(s_data["Дата операции"], "%d.%m.%Y %H:%M:%S") >= end_date
        if category in str(s_data["Категория"]) and valid_end_day and valid_start_day:
            all_buys.append(s_data)
    logger.info("Сформирован файл в формате DataFrame")
    return pd.DataFrame(all_buys)
