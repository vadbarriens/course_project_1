from datetime import datetime
from typing import Any
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.utils import (filter_date_operations, get_data_from_excel,
                       greeting_user, operations_cards, stock_prices,
                       top_five_transactions)


@patch("builtins.open", new_callable=mock_open, read_data=b"\x3c\x80\x00\x00\x00")
@patch("pandas.read_excel")
def test_get_data_from_excel(mock_read_excel: Any, mock_file: Any) -> None:
    mock_read_excel.return_value = pd.DataFrame({"amount": [100], "currency": ["USD"]})
    transactions = get_data_from_excel("data/transactions.xlsx")
    assert transactions == [{"amount": 100, "currency": "USD"}]


@patch("builtins.open", side_effect=FileNotFoundError)
def test_not_found_excel(mock_file: Any) -> None:
    transactions = get_data_from_excel("data/transactions.xlsx")
    assert transactions == []


def test_filter_date_operations(transactions: pd.DataFrame) -> None:
    result_df = filter_date_operations(transactions, "2021-12-29 11:15:21")
    assert len(result_df) == 2


@pytest.mark.parametrize(
    ("now_datetime", "expected_greeting"),
    [
        (datetime(2024, 1, 1, hour=6, minute=0), "Доброе утро"),
        (datetime(2024, 1, 1, hour=14, minute=0), "Добрый день"),
        (datetime(2024, 1, 1, hour=20, minute=0), "Добрый вечер"),
        (datetime(2024, 1, 1, hour=3, minute=0), "Доброй ночи"),
    ],
)
@patch("src.utils.datetime")
def test_get_greeting(
    mocked_datetime: Any, now_datetime: Any, expected_greeting: str
) -> None:
    mocked_datetime.now.return_value = now_datetime
    assert greeting_user() == expected_greeting


def test_operations_cards(transactions: pd.DataFrame) -> None:
    assert operations_cards(transactions) == [
        {"last_digits": "7197", "total_spent": 600.00, "cashback": 6.00}
    ]


def test_top_five_transactions(small_operations: pd.DataFrame) -> None:
    assert top_five_transactions(small_operations) == [
        {
            "date": "20.09.2021 12:45:12",
            "amount": 200.00,
            "category": "Супермаркеты",
            "description": "Магнит",
        }
    ]


@patch("requests.get")
def test_stock_prices(mock_convert: Any):
    mock_convert.return_value.status_code = 200
    mock_convert.return_value.json.return_value = {
        "data": [{"symbol": "AAPL", "close": 1.0}]
    }
    assert stock_prices() == [{"stock": "AAPL", "price": 1.0}]
