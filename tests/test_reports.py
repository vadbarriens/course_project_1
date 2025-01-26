from typing import Any
from unittest.mock import mock_open, patch

import pandas as pd

from src.reports import recording_data, spending_by_category


def test_spending_by_category(transactions: pd.DataFrame) -> None:
    result_df = spending_by_category(transactions, "Супермаркеты", "2021-11-15 12:00:00")
    assert len(result_df) == 3


def test_spending_by_category_no_data(transactions: pd.DataFrame) -> None:
    result_df = spending_by_category(transactions, "Супермаркеты")
    assert len(result_df) == 0


@patch("builtins.open", new_callable=mock_open)
def test_recording_data_decorator(mock_file: Any):
    test_data = pd.DataFrame({"name": ["Alice", "Bob"], "age": [25, 30]})

    @recording_data("test_report.json")
    def function():
        return test_data

    returned_value = function()

    pd.testing.assert_frame_equal(returned_value, test_data)
