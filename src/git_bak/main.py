from pathlib import Path

from git_bak import command, handlers
from git_bak.args import parser
from git_bak.exceptions import BackupError, RestoreError
from git_bak.logging import logger, setup_logging

HOME = Path.home()
LOG_FILE = "git_{}.log"


def main():
    try:
        args = parser()
        setup_logging(
            HOME / LOG_FILE.format(args.command), args.log_level, args.verbose
        )
        logger.info(f"{args.command.capitalize()} Operation started")
        commands = command.factory(args.command, args)
        handler = handlers.factory(args.command)
        for cmd in commands:
            handler.handle(cmd)
        logger.info(f"{args.command.capitalize()} Operation successfully completed")
    except BackupError as e:
        logger.error(e)
    except RestoreError as e:
        logger.error(e)
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
