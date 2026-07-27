import logging
from pathlib import Path
from datetime import datetime


class Logger:
    """
    Centralized logger utility.

    Creates log files under:
        reports/logs/

    Usage:
        from utils.logger import Logger

        logger = Logger.get_logger(__name__)
        logger.info("Message")
    """

    @staticmethod
    def get_logger(name: str = "AutomationFramework") -> logging.Logger:
        logger = logging.getLogger(name)

        # Prevent duplicate handlers
        if logger.handlers:
            return logger

        logger.setLevel(logging.INFO)

        log_directory = Path("reports") / "logs"
        log_directory.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_directory / f"automation_{timestamp}.log"

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
        )

        # File Handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger