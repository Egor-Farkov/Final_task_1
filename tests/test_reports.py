from unittest.mock import patch

import pandas
import pandas as pd
import pytest

from src.reports import log, reading_financial_from_reports_excel, spending_by_category


def test_reading_financial_from_reports_excel() -> None:
    """
    [Тест] Функция для считывания финансовых операций из Excel выдает список словарей с транзакциями.
    """

    success_test = reading_financial_from_reports_excel()
    assert isinstance(success_test, pandas.core.frame.DataFrame)

    with pytest.raises(ValueError):
        reading_financial_from_reports_excel("")

    with patch("pandas.read_excel") as read_pd:
        read_pd.return_value = "test_data"
        with pytest.raises(Exception):
            reading_financial_from_reports_excel("")


def test_spending_by_category() -> None:
    """[Тест] Функция затрат по категории возвращающая в формате DataFrame"""

    success_tests = spending_by_category()
    assert isinstance(success_tests, str)


def test_decorators() -> None:
    """Тестирование декоратора."""

    @log()
    def one() -> pd.DataFrame:
        return pd.DataFrame([{1: ''}])

    assert isinstance(one(), str)
