import os
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from git_bak.args import CliArguments
from git_bak.requests import BackupRequest, RestoreRequest, _iter_valid_entries, factory


def make_files(tmp_path):
    # Create 3 bundle files
    file1 = tmp_path / "file1.bundle"
    file2 = tmp_path / "file2.bundle"
    file3 = tmp_path / "file3.bundle.19700101_000000"  # file with timestamp extension

    file1.write_text("data")
    file2.write_text("data")
    file3.write_text("data")

    # Set explicit modification times
    os.utime(file1, (time.time(), 100))  # mtime = 100
    os.utime(file2, (time.time(), 200))  # mtime = 200 - most recent file
    os.utime(file3, (time.time(), 0))  # mtime = 50

    return file1, file2, file3


def test_iter_valid_entries_filters_and_yields(tmp_path):
    included_dir = tmp_path / "project1"
    excluded_dir = tmp_path / "project2"
    file_entry = tmp_path / "file"

    file_entry.write_text("data")

    included_dir.mkdir()
    excluded_dir.mkdir()

    mock_filter_fn = MagicMock()
    mock_filter_fn.side_effect = lambda path: path if path.name == "project1" else None

    result_using_include = list(
        _iter_valid_entries(
            tmp_path,
            include=["project1", "project2"],
            exclude=None,
            extra_filter_fn=mock_filter_fn,
        )
    )

    result_using_exclude = list(
        _iter_valid_entries(
            tmp_path, include=None, exclude=["project2"], extra_filter_fn=mock_filter_fn
        )
    )
    # included_dir is the only dir that passes
    assert result_using_include == [included_dir]
    assert result_using_exclude == [included_dir]
    mock_filter_fn.assert_called()


def test_backup_request_has_git_dir(tmp_path):
    path = tmp_path / ".git"
    path.mkdir()

    result = BackupRequest.has_git_dir(tmp_path)
    assert result == tmp_path


def test_backup_request_has_git_dir_returns_none(tmp_path):
    result = BackupRequest.has_git_dir(tmp_path)
    assert result is None


def test_backup_request_create(tmp_path, monkeypatch):
    project1 = tmp_path / "source" / "project1"
    destination = tmp_path / "destination"

    project1.mkdir(parents=True)
    destination.mkdir()

    monkeypatch.setattr(
        "git_bak.requests._iter_valid_entries", lambda *_, **__: iter([project1])
    )

    result = BackupRequest.create(
        source=tmp_path / "source",
        destination=destination,
        include=None,
        exclude=None,
    )

    assert all(isinstance(r, BackupRequest) for r in result)
    assert result[0].source == project1
    assert result[0].destination == destination


def test_restore_request_find_bundle_latest(tmp_path):
    file1, file2, file3 = make_files(tmp_path)

    result = RestoreRequest.find_bundle(tmp_path, timestamp=None)
    assert result == file2


def test_restore_request_find_bundle_by_timestamp(tmp_path):
    file1, file2, file3 = make_files(tmp_path)
    timestamp = datetime.fromtimestamp(0, tz=timezone.utc).strftime("%Y%m%d_%H%M%S")

    result = RestoreRequest.find_bundle(tmp_path, timestamp=timestamp)

    assert result == file3


def test_restore_request_find_bundle_returns_none(tmp_path):
    file1, file2, file3 = make_files(tmp_path)
    timestamp = datetime.fromtimestamp(70, tz=timezone.utc).strftime("%Y%m%d_%H%M%S")

    result = RestoreRequest.find_bundle(tmp_path, timestamp=timestamp)

    assert result is None


def test_restore_request_create(tmp_path, monkeypatch):
    project1 = tmp_path / "source" / "project1"
    destination = tmp_path / "destination"

    project1.mkdir(parents=True)
    destination.mkdir()

    monkeypatch.setattr(
        "git_bak.requests._iter_valid_entries", lambda *_, **__: iter([project1])
    )

    result = RestoreRequest.create(
        source=tmp_path / "source",
        destination=destination,
        include=None,
        exclude=None,
        timestamp=None,
    )

    assert all(isinstance(r, RestoreRequest) for r in result)
    assert result[0].source == project1
    assert result[0].destination == destination


def test_factory_calls_backup_request_create(monkeypatch):
    mock_create = MagicMock(return_value=["mocked"])
    monkeypatch.setattr("git_bak.requests.BackupRequest.create", mock_create)

    args = CliArguments(
        command="backup",
        source=Path("src"),
        destination=Path("dst"),
        include=["include"],
        exclude=None,
        verbose=False,
        log_to_file=False,
        quiet=False,
        timestamp=None,
    )

    result = factory("backup", args)

    mock_create.assert_called_once_with(Path("src"), Path("dst"), ["include"], None)
    assert result == ["mocked"]


def test_factory_calls_restore_request_create(monkeypatch):
    mock_create = MagicMock(return_value=["mocked"])
    monkeypatch.setattr("git_bak.requests.RestoreRequest.create", mock_create)

    args = CliArguments(
        command="backup",
        source=Path("src"),
        destination=Path("dst"),
        include=["include"],
        exclude=None,
        verbose=False,
        log_to_file=False,
        quiet=False,
        timestamp="20250101_101010",
    )

    result = factory("restore", args)

    mock_create.assert_called_once_with(
        Path("src"), Path("dst"), ["include"], None, "20250101_101010"
    )
    assert result == ["mocked"]
