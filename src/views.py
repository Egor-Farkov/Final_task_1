from src.utils import (
    get_stocks_price,
    getting_a_date_period,
    main_all_info_on_cards,
    reading_financial_transactions_from_excel,
    return_exchange_rates,
    return_of_top_transactions,
    return_welcome_text_by_date,
)


def page_main(date: str) -> dict:
    """
    Функция главной страницы возвращает основную информацию.
    :param date: Входящая дата.
    :return: Json объект содержащий информацию.
    """
    period_date = getting_a_date_period(date)
    struct_file_json = reading_financial_transactions_from_excel(period_date)
    json_response = {
        "greeting": return_welcome_text_by_date(date),
        "cards": main_all_info_on_cards(struct_file_json),
        "top_transactions": return_of_top_transactions(struct_file_json),
        "currency_rates": return_exchange_rates(),
        "stock_prices": get_stocks_price(),
    }
    return json_response
