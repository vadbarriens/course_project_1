import json

from src.services import transactions_by_phone_numbers


def test_transactions_by_phone_numbers(num_operations_list) -> None:
    result = [
        {
            "Дата операции": "01.01.2021 18:08:23",
            "Дата платежа": "01.01.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": -815.68,
            "Валюта операции": "RUB",
            "Сумма платежа": -815.68,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": 5411.0,
            "Описание": "Тинькофф Мобайл +7 995 555-55-55",
            "Бонусы (включая кэшбэк)": 16,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 815.68,
        },
    ]
    assert transactions_by_phone_numbers(num_operations_list) == json.dumps(result, ensure_ascii=False)
