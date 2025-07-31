from abc import ABC, abstractmethod
from pathlib import Path

from git_bak import git
from git_bak.command import BackupCommand, Command, RestoreCommand
from git_bak.exceptions import BackupError, RestoreError
from git_bak.logging import logger


class Handler[T: Command](ABC):
    """Handler abstraction"""

    @abstractmethod
    def handle(self, command: T) -> None:
        raise NotImplementedError


class BackupHandler(Handler[BackupCommand]):
    def handle(self, command: BackupCommand) -> None:
        """Creates a Git bundle from a source project and stores at a desired location."""
        logger.info(f"Backup Git repository : {command.source.name}")
        try:
            git.backup(command.source, command.destination)
        except BackupError as e:
            logger.error(e)


class RestoreHandler(Handler[RestoreCommand]):
    def handle(self, command: RestoreCommand) -> None:
        logger.info(f"Restore Git repository : {command.source.name}")
        try:
            bundle_path = self._find_bundle(command.source, command.timestamp)
            git.restore(bundle_path, command.destination)
        except RestoreError as e:
            logger.error(e)

    @staticmethod
    def _find_bundle(path: Path, timestamp: str | None) -> Path:
        try:
            if timestamp is None:
                return max(path.iterdir(), key=lambda f: f.stat().st_mtime)
            return next((f for f in path.iterdir() if timestamp in str(f)))
        except ValueError:
            raise RestoreError(f"No Git bundle found : {path}")
        except StopIteration:
            raise RestoreError(
                f"No Git bundle found for timestamp {timestamp} : {path}"
            )


def factory(command: str) -> Handler:
    """Handler factory that returns a concrete Handler based on the command argument."""
    if command == "backup":
        return BackupHandler()
    if command == "restore":
        return RestoreHandler()
