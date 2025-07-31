import subprocess
from datetime import datetime, timezone
from pathlib import Path

from git_bak.exceptions import (
    BackupError,
    GitRepoHasNoCommits,
    GitRepoInvalid,
    RestoreError,
)
from git_bak.logging import logger

now = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M")


def is_valid_git_repo(path: Path) -> None:
    """Check if project has valid Git repository"""
    repo_name = path.name
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logger.debug(f"Found Git repo : {repo_name}")
        logger.debug(result)
    except subprocess.CalledProcessError:
        raise GitRepoInvalid(f"No valid git repo found, skipping : {repo_name}")


def has_commits(path: Path) -> None:
    """Check if the Git repository has any commits."""
    repo_name = path.name
    logger.debug(f"Checking if Git repo has any commits : {repo_name}")
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--verify", "HEAD"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        logger.debug(f"Git repo has commits: {repo_name}")
        logger.debug(f"{result}")
    except subprocess.CalledProcessError:
        raise GitRepoHasNoCommits(f"Git repo has not commits, skipping : {repo_name}")


def is_valid_bundle(path: Path) -> bool:
    """Check if Git bundle is valid."""
    try:
        logger.debug(f"Checking if Git bundle is valid : {path.name}")
        result = subprocess.run(
            ["git", "bundle", "verify", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        logger.debug(f"{result}")
    except subprocess.CalledProcessError as e:
        raise GitRepoInvalid(f"Git bundle is not valid for restore : {path.name}")


def backup(source: Path, destination: Path) -> None:
    """Creating Git repository bundle."""
    repo_name = source.name
    try:
        is_valid_git_repo(source)
        has_commits(source)
        bundle_filename = f"{repo_name}_{now}.bundle"
        bundle_backup_dir = destination / repo_name
        bundle_backup_dir.mkdir(parents=False, exist_ok=True)
        bundle_path = bundle_backup_dir / bundle_filename
        result = subprocess.run(
            [
                "git",
                "-C",
                str(source),
                "bundle",
                "create",
                str(bundle_path),
                "--all",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        logger.info(f"Successfully created Git bundle : {bundle_path}")
        logger.debug(f"{result}")
    except GitRepoInvalid as e:
        logger.warning(e)
    except GitRepoHasNoCommits as e:
        logger.warning(e)
    except subprocess.CalledProcessError as e:
        raise BackupError(f"Failed to create bundle for {repo_name} : {e}")


def restore(source: Path, destination: Path) -> None:
    """Restores Git bundle by cloning the Git bundle."""
    try:
        is_valid_bundle(source)
        # Gets the name of the repo from the source path
        name = source.name.split("_", 1)[0]
        # sets the restore destination to name of the repo
        restore_destination = destination / name
        result = subprocess.run(
            ["git", "clone", str(source), str(restore_destination)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        logger.info(f"Successfully restored Git bundle : {source.name}")
        logger.debug(result)
    except GitRepoInvalid as e:
        logger.warning(e)
    except subprocess.CalledProcessError as e:
        raise RestoreError(f"Failed to restore Git bundle : {e}")
