import json
import logging
import re

import pandas as pd

from config import ROOT_DIR

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(ROOT_DIR + "/logs/services.log", "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(module)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


def read_file_excel(path: str = ROOT_DIR + "/data/operations.xlsx") -> list[dict]:
    """Функция для чтения файла Excel"""
    try:
        df = pd.read_excel(path)
        record = df.to_dict("records")
        logger.info(f"Файл по директории {path} найден и обработан")
        return record
    except FileNotFoundError as e:
        logger.error("Ошибка, файл не найден")
        raise e
    except Exception as e:
        logger.error(f"Ошибка {e}")
        raise e


def get_search_result(word: str | None) -> str:
    """Функция получает запрос поиска от пользователя"""
    if word:
        data_excel = read_file_excel()
        get_string = [data for data in data_excel if word in str(data["Категория"]) or word in str(data["Описание"])]
        logger.info("Данные получены успешно")
        return json.dumps(get_string)
    logger.error("Передано пустое значение")
    raise ValueError("Передано пустое значение")


def search_mobile_excel() -> str:
    """Функция для поиска мобильных номеров в поле Категория"""
    data_mobile = []
    data_excel = read_file_excel()
    for data in data_excel:
        re_search = re.search(r"\+7 \d{3} \d{2,3}-\d{2}-\d{2}", str(data["Категория"]))
        if re_search:
            data_mobile.append(data)
    logger.info("Данные считаны успешно")
    return json.dumps(data_mobile)


def search_transaction_to_people() -> str:
    """Функция поиска переводов физическим лицам"""
    sent_transaction = []
    data_excel = read_file_excel()
    for data in data_excel:
        re_search = re.search(r"^[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\.$", str(data["Описание"]), re.I)
        if "Переводы" in str(data["Категория"]) and re_search:
            sent_transaction.append(data)
    logger.info("Данные по переводам считаны успешно")
    return json.dumps(sent_transaction)
