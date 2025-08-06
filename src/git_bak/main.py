from pathlib import Path

from git_bak import handlers, requests
from git_bak.args import parser
from git_bak.git import Git
from git_bak.logging import logger, setup_logging
from git_bak.runners import SubprocessRunner

HOME = Path.home()
LOG_FILE = "git_{}.log"


def main():
    try:
        args = parser()
        setup_logging(
            HOME / LOG_FILE.format(args.command),
            args.log_to_file,
            args.verbose,
            args.quiet,
        )
        runner = SubprocessRunner()
        git = Git(runner)
        logger.info(f"Source directory : {args.source}")
        logger.info(f"Destination directory : {args.destination}")
        logger.debug(f"Include filter: {args.include}")
        logger.debug(f"Exclude fitler: {args.exclude}")
        logger.debug(f"Timestamp fitler: {args.timestamp}") if args.timestamp else None
        reqs = requests.factory(args.command, args)
        if not reqs:
            logger.warning(
                "No Git Requests generated for Git Handlers to process. Check source directory."
            )
        handler = handlers.factory(args.command, git)
        for request in reqs:
            logger.debug(request)
            handler.handle(request)
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    main()
