import json
import logging
import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))

rel_file_path = os.path.join(current_dir, "../logs/services.log")
abs_file_path = os.path.abspath(rel_file_path)

logger = logging.getLogger("services")
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(abs_file_path, "w", encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(funcName)s %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def transactions_by_phone_numbers(operations: list) -> json:
    """Возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера"""
    logger.info("Ищем транзакции содержащие мобильные номера")
    phone_pattern = re.compile(
        r"\b(?:\+7|8)?\s*(909|919|929|949|959|970|980|997|999|\d{3})\s*\d{3}\s*[-]?\s*\d{2}\s*[-]?\s*\d{2}\b"
    )
    filtered_transactions = [
        operation
        for operation in operations
        if "Описание" in operation and phone_pattern.search(operation["Описание"])
    ]
    return json.dumps(filtered_transactions, ensure_ascii=False)
