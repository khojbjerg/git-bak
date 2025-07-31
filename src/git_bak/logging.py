import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

logger = logging.getLogger("git-bundler")


def setup_logging(log_file: Path, level: str, verbose: bool = False) -> None:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=10)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    handlers = [file_handler]

    if verbose:
        handlers.append(console_handler)

    logging.basicConfig(level=level, handlers=handlers)
