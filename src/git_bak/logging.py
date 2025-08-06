import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

logger = logging.getLogger("git-bak")


def setup_logging(
    log_file: Path,
    log_to_file: bool = False,
    verbose: bool = False,
    quiet: bool = False,
) -> None:
    minimal_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    debug_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s"
    )

    formatter = debug_formatter if verbose else minimal_formatter

    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=10)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    log_level = "DEBUG" if verbose else "INFO"

    handlers = []

    if log_to_file:
        handlers.append(file_handler)

    if quiet is False:
        handlers.append(console_handler)

    logging.basicConfig(level=log_level, handlers=handlers)
