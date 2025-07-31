import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Arguments:
    command: str
    source: Path
    destination: Path
    include: list[str]
    exclude: list[str]
    log_level: str
    verbose: bool
    timestamp: str | None = None


def parser() -> Arguments:
    """Parse argparse arguments and returns a custom Arguments dataclass object."""
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help=f"Path to directory containing Git projects",
    )
    common_parser.add_argument(
        "--destination",
        type=Path,
        required=True,
        help=f"Directory to store bundle files",
    )
    common_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help=f"Set the logging level.",
    )
    common_parser.add_argument(
        "--include",
        nargs="+",
        help="Optional list of project folder names to include. Seperate project names by space (defaults to None, which is all projects in projects-dir)",
    )
    common_parser.add_argument(
        "--exclude",
        nargs="+",
        help="Optional list of project folder names to exclude. Seperate project names by space (defaults to None which excludes no projects in projects-dir)",
    )
    common_parser.add_argument("--verbose", action="store_true")

    parser = argparse.ArgumentParser(
        description=f"Backup/Restore Git repositories. Log files stored in {Path.home() / 'git_backup|restore.log'}",
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
        type=str,
        help="Optional timestamp str value of specific backup to restore. e.g 20250731_1000 (defaults to None which will take the latest backup)",
    )

    args = parser.parse_args()

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
    return Arguments(
        args.command,
        args.source,
        args.destination,
        args.include,
        args.exclude,
        args.log_level,
        args.verbose,
        args.timestamp if hasattr(args, "timestamp") else None,
    )
