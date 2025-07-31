import typing as t
from abc import ABC
from dataclasses import dataclass
from pathlib import Path

from git_bak.args import Arguments
from git_bak.logging import logger


class Command(ABC):
    pass


@dataclass
class BackupCommand(Command):
    source: Path
    destination: Path

    @classmethod
    def create(
        cls,
        source: Path,
        destination: Path,
        include: list[str] | None,
        exclude: list[str] | None,
    ) -> list[t.Self]:
        """Create Command instances from function parameters."""
        logger.info(f"Source directory : {source}")
        logger.info(f"Destination directory : {destination}")
        commands = []
        for e in source.iterdir():
            name = e.name
            logger.debug(f"Creating Command object for : {e}")
            if e.is_dir() is False:
                logger.debug(f"Not a Project directory, skipping : {name}")
                continue

            if include and name not in include:
                continue

            if exclude and name in exclude:
                logger.info(f"Project directory excluded : {name}")
                continue
            command = BackupCommand(source=e, destination=destination)
            logger.debug(command)
            commands.append(command)
        return commands


@dataclass
class RestoreCommand:
    source: Path
    destination: Path
    timestamp: str | None = None

    @classmethod
    def create(
        cls,
        source: Path,
        destination: Path,
        include: list[str] | None,
        exclude: list[str] | None,
        timestamp: str | None,
    ) -> list[t.Self]:
        logger.info(f"Source directory : {source}")
        logger.info(f"Destination directory : {destination}")
        commands = []
        for e in source.iterdir():
            name = e.name
            logger.debug(f"Creating Command object for : {e}")
            if e.is_dir() is False:
                logger.debug(f"Not a repository directory, skipping : {name}")
                continue

            if include and name not in include:
                continue

            if exclude and name in exclude:
                logger.info(f"Git repository directory excluded : {name}")
                continue

            command = RestoreCommand(
                source=e, destination=destination, timestamp=timestamp
            )
            logger.debug(command)
            commands.append(command)
        return commands


def factory(command: str, args: Arguments) -> list[Command]:
    if command == "backup":
        return BackupCommand.create(
            args.source, args.destination, args.include, args.exclude
        )
    if command == "restore":
        return RestoreCommand.create(
            args.source, args.destination, args.include, args.exclude, args.timestamp
        )
