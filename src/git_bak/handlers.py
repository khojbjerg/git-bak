from abc import ABC, abstractmethod

from git_bak.exceptions import (
    GitBundleError,
    GitRepoHasNoCommits,
    GitRepoInvalid,
    RestoreError,
)
from git_bak.git import Git
from git_bak.logging import logger
from git_bak.requests import BackupRequest, Request, RestoreRequest


class Handler[T: Request](ABC):
    """Handler abstraction"""

    @abstractmethod
    def handle(self, request: T) -> None:
        raise NotImplementedError


class BackupHandler(Handler[BackupRequest]):
    def __init__(self, git: Git):
        self._git = git

    def handle(self, request: BackupRequest) -> None:
        """Creates a Git bundle from a source project and stores at a desired location."""
        logger.info(f"Starting backup for: {request.source}")
        try:
            result = self._git.create_bundle(request.source, request.destination)
            logger.info(f"Backup completed for: {request.source} -> {result}")
        except GitRepoInvalid as e:
            logger.warning(f"{request.source} Skipping: {e}")
        except GitRepoHasNoCommits as e:
            logger.warning(f"{request.source} Skipping: {e}")
        except GitBundleError as e:
            logger.error(f"{request.source} {e}")


class RestoreHandler(Handler[RestoreRequest]):
    def __init__(self, git: Git):
        self._git = git

    def handle(self, request: RestoreRequest) -> None:
        logger.info(f"Starting restore for: {request.source}")
        try:
            result = self._git.clone_bundle(request.source, request.destination)
            logger.info(f"Restore completed for: {request.source} -> {result}")
        except RestoreError as e:
            logger.warning(f"{request.source} {e}")


def factory(command: str, git: Git) -> Handler:
    """Handler factory that returns a concrete Handler based on the command argument."""
    if command == "backup":
        return BackupHandler(git)
    if command == "restore":
        return RestoreHandler(git)
