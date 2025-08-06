import argparse
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CliArguments:
    command: str
    source: Path
    destination: Path
    include: list[str] | None
    exclude: list[str] | None
    verbose: bool
    log_to_file: bool
    quiet: bool
    timestamp: str | None = None


def validate_timestamp(value: str) -> str:
    pattern = r"^\d{8}_\d{6}$"  # YYYYMMDD_HHMMSS
    if not re.match(pattern, value):
        raise argparse.ArgumentTypeError(
            f"Invalid timestamp format: '{value}'. Expected format: YYYYMMDD_HHMMSS"
        )
    return value


def parser(argv: list[str] | None = None) -> CliArguments:
    """Parse argparse arguments and returns a custom Arguments dataclass object."""
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Path to the source directory (where the repos are located or backed up).",
    )
    common_parser.add_argument(
        "--destination",
        type=Path,
        required=True,
        help="Path to the destination directory (where to store or restore repositories).",
    )
    common_parser.add_argument(
        "--include",
        nargs="+",
        help="Optional List of repository names to include. Seperate names by space.",
    )
    common_parser.add_argument(
        "--exclude",
        nargs="+",
        help="Optional List of repository names to exclude. Seperate names by space.",
    )
    common_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Optional Enable debug logging.",
    )
    common_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Optional Suppress console output (StreamHandler) (useful for cron).",
    )
    common_parser.add_argument(
        "--log-to-file",
        action="store_true",
        help=f"Optional Enable file logging. Log file location: {Path.home() / 'git_backup|restore.log'}",
    )

    parser = argparse.ArgumentParser(
        description="Backup/Restore Git repositories.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "backup", help="Performs backup of Git repositories.", parents=[common_parser]
    )

    restore_parser = subparsers.add_parser(
        "restore", help="Performs restore of Git repositories.", parents=[common_parser]
    )
    restore_parser.add_argument(
        "--timestamp",
        type=validate_timestamp,
        help="Restore from a specific backup timestamp (e.g 20250731_1000). If not provided, restores the latest backup.",
    )

    args = parser.parse_args(argv)

    if args.source == args.destination:
        parser.error("Source and destination can't be the same directory.")

    if args.include and args.exclude:
        parser.error("You cannot use both --include and --exclude at the same time.")

    source: Path = args.source
    destination: Path = args.destination

    if source.is_dir() is False:
        parser.error(f"Source directory does not exists : {source}")

    if destination.is_dir() is False:
        parser.error(f"Destination directory does not exists : {destination}")

    if args.include:
        includes: list[str] = args.include
        missing = [name for name in includes if not (source / name).is_dir()]
        if missing:
            parser.error(
                f"Included project(s) not found in {source}: {', '.join(missing)}"
            )

    return CliArguments(
        args.command,
        args.source,
        args.destination,
        args.include,
        args.exclude,
        args.verbose,
        args.log_to_file,
        args.quiet,
        args.timestamp if hasattr(args, "timestamp") else None,
    )
