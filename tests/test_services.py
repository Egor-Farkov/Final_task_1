from unittest.mock import patch

import pytest

from src.services import get_search_result, read_file_excel, search_mobile_excel, search_transaction_to_people


def test_read_file_excel() -> None:
    """Тест функции для чтения файла Excel"""
    with pytest.raises(FileNotFoundError):
        read_file_excel("")
    with pytest.raises(Exception):
        with patch("pd.read_excel") as pd_mock:
            pd_mock.return_value = ""
            read_file_excel("")

    with patch("pandas.core.frame.DataFrame.to_dict") as pd_mock:
        pd_mock.return_value = [{}]
        assert read_file_excel() == [{}]


def test_get_search_result() -> None:
    """Тест функции, которая получает запрос поиска от пользователя"""
    with pytest.raises(ValueError):
        get_search_result(None)

    with patch("json.dumps", return_value="[{}]"):
        assert get_search_result("asddssd") == "[{}]"


def test_search_mobile_excel() -> None:
    """Тест функции для поиска мобильных номеров в поле Категория"""
    with patch("json.dumps", return_value="[{}]"):
        assert search_mobile_excel() == "[{}]"


def test_search_transaction_to_people() -> None:
    """Тест поиска переводов физическим лицам"""
    with patch("json.dumps", return_value="[{}]"):
        assert search_transaction_to_people() == "[{}]"
