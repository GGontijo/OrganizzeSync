import logging
from datetime import datetime
from typing import Literal

class Logger:
    def __init__(self, log_file: str) -> None:
        self.log_file = log_file
        self.setup_logging()

    def setup_logging(self) -> None:
        logging.basicConfig(level=logging.INFO, filename=self.log_file, encoding='utf-8', format='%(asctime)s | %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s | %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)

    def log(self, level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], message: str) -> None:
        getattr(logging, level.lower())(message)
