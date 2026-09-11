import logging
from datetime import datetime

logging.basicConfig(filename="proxy.log", level=logging.INFO)


def log_request(method: str, path: str, status_code: int) -> None:
    logging.info(f"{datetime.now()} - {method} {path} - Status: {status_code}")


def log_info(msg: str) -> None:
    logging.info(f"{datetime.now()} - {msg}")


def log_error(msg: str) -> None:
    logging.error(f"{datetime.now()} - {msg}")
