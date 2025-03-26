import pandas as pd
import re
from collections import Counter


from config import ROOT_DIR

# print(excel_data.shape)
# print(excel_data)
# print(type(excel_data))

df = pd.read_excel(ROOT_DIR + '/data/operations.xlsx')

def transaction_mobile_excel(data: str) -> list[dict]:
    """Функция для считывания данных из Excel"""
    spend_by_mobile = df.loc[df['Категория'] == 'Мобильная связь']
    return list[spend_by_mobile]


def filter_transaction(datas: list[dict], word: str) -> list[dict]:
    """
    Функция принимает список словарей с данными о банковских операциях и строку поиска,
    возвращает список словарей, у которых в описании есть данная строка.
    :param datas: Список словарей с данными.
    :param word: Поисковое слово.
    :return: Список словарей, у которых в описании есть данная строка.
    """
    return [data for data in datas if re.search(word, data['Категория'], re.I)]

print(filter_transaction(transaction_mobile_excel('Категория'), 'Мобильная связь'))

# def transaction_mobile_excel(path: str) -> list[dict]:
#     spend_by_mobile = pd.read_excel(path).to_dict("Категория")
#     print(spend_by_mobile)



