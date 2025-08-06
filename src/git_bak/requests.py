import typing as t
from abc import ABC
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from git_bak.args import CliArguments


def _iter_valid_entries(
    base_path: Path,
    *,
    include: list[str] | None,
    exclude: list[str] | None,
    extra_filter_fn: t.Callable[[Path], Path | None],
) -> t.Iterator[Path]:
    """Iterates base_path directory and apply filters to yield paths if valid."""
    for entry in base_path.iterdir():
        name = entry.name

        if include and name not in include:
            continue
        if exclude and name in exclude:
            continue
        if not entry.is_dir():
            continue
        path = extra_filter_fn(entry)
        if not path:
            continue
        yield path


class Request(ABC):
    pass


@dataclass
class BackupRequest(Request):
    source: Path
    destination: Path

    @staticmethod
    def has_git_dir(path: Path) -> Path | None:
        """Check if .git directory exists. It does not check Git repository validity."""
        if (path / ".git").is_dir():
            return path

    @classmethod
    def create(
        cls,
        source: Path,
        destination: Path,
        include: list[str] | None,
        exclude: list[str] | None,
    ) -> list[t.Self]:
        """Create from function parameters."""
        return [
            cls(source=entry, destination=destination)
            for entry in _iter_valid_entries(
                source,
                include=include,
                exclude=exclude,
                extra_filter_fn=cls.has_git_dir,
            )
        ]


@dataclass
class RestoreRequest(Request):
    source: Path
    destination: Path

    @staticmethod
    def find_bundle(path: Path, *, timestamp: str | None) -> Path | None:
        if timestamp:
            return next(
                (f for f in path.iterdir() if f.name.endswith(f"bundle.{timestamp}")),
                None,
            )
        return max(path.iterdir(), default=None, key=lambda f: f.stat().st_mtime)

    @classmethod
    def create(
        cls,
        source: Path,
        destination: Path,
        include: list[str] | None,
        exclude: list[str] | None,
        timestamp: str | None,
    ) -> list[t.Self]:
        return [
            cls(source=entry, destination=destination)
            for entry in _iter_valid_entries(
                source,
                include=include,
                exclude=exclude,
                extra_filter_fn=partial(cls.find_bundle, timestamp=timestamp),
            )
        ]


def factory(command: str, args: CliArguments) -> list[Request]:
    if command == "backup":
        return BackupRequest.create(
            args.source, args.destination, args.include, args.exclude
        )
    if command == "restore":
        return RestoreRequest.create(
            args.source, args.destination, args.include, args.exclude, args.timestamp
        )
