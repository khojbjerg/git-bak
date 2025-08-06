from datetime import datetime, timezone
from pathlib import Path

from git_bak.exceptions import (
    GitBundleError,
    GitRepoHasNoCommits,
    GitRepoInvalid,
    RunnerError,
)
from git_bak.runners import CommandRunner

now = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")


class Git:
    def __init__(self, runner: CommandRunner):
        self._runner = runner

    def assert_valid_repo(self, path: Path) -> None:
        """
        Asserts that given path is a valid Git repository.
        Raises if not.
        """
        try:
            cmd = ["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"]
            self._runner.run(cmd)
        except RunnerError as e:
            raise GitRepoInvalid(f"Git repository invalid {e}")

    def assert_has_commits(self, path: Path) -> None:
        """
        Asserts the Git repository has any commits.
        Raises if not.
        """
        try:
            cmd = ["git", "-C", str(path), "rev-parse", "--verify", "HEAD"]
            self._runner.run(cmd)
        except RunnerError as e:
            raise GitRepoHasNoCommits(f"Git repository has no commits {e}")

    def assert_bundle(self, path: Path) -> None:
        """
        Asserts Git bundle is valid.
        Raises if not.
        """
        try:
            cmd = ["git", "bundle", "list-heads", str(path)]
            self._runner.run(cmd)
        except RunnerError as e:
            raise GitRepoInvalid(f"Git bundle not a valid {e}")

    def create_bundle(self, source: Path, destination: Path) -> str:
        """Creating Git repository bundle."""
        repo_name = source.name
        try:
            bundle_filename = f"{repo_name}.bundle.{now}"
            self.assert_valid_repo(source)
            self.assert_has_commits(source)
            bundle_backup_dir = destination / repo_name
            bundle_backup_dir.mkdir(parents=False, exist_ok=True)
            bundle_path = bundle_backup_dir / bundle_filename
            cmd = [
                "git",
                "-C",
                str(source),
                "bundle",
                "create",
                str(bundle_path),
                "--all",
            ]
            self._runner.run(cmd)
            return str(bundle_path)
        except RunnerError as e:
            raise GitBundleError(f"Failed: Unable to create Git bundle {e}")

    def clone_bundle(self, source: Path, destination: Path) -> str:
        """Restores Git bundle by cloning the Git bundle."""
        try:
            self.assert_bundle(source)
            # Gets the name of the repo from the source path, removes .bundle.YYYYMMDD_HHMM extension.
            name = source.name.split(".", 1)[0]
            # sets the restore destination to name of the repo
            restore_destination = destination / name
            cmd = ["git", "clone", str(source), str(restore_destination)]
            self._runner.run(cmd)
            return str(restore_destination)
        except RunnerError as e:
            raise GitBundleError(f"Failed: Unable to clone Git bundle {e}")
