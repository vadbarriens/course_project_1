import pandas as pd

from src.reports import spending_by_category
from src.services import transactions_by_phone_numbers
from src.utils import get_data_from_excel
from src.views import web_main

transactions = get_data_from_excel("../data/operations.xlsx")
transactions_df = pd.read_excel("../data/operations.xlsx")


def main(user_date: str, operations: list, operations_df: pd.DataFrame, user_category: str) -> None:
    """Вызывает результаты всех реализованных функций"""
    print(web_main(user_date))
    print(transactions_by_phone_numbers(operations))
    print(spending_by_category(operations_df, user_category, user_date))


if __name__ == "__main__":
    main("2021-01-10 12:00:00", transactions, transactions_df, "Супермаркеты")
