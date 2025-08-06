import argparse

import pytest

from git_bak.args import CliArguments, parser, validate_timestamp


def test_validate_timestamp():
    value = validate_timestamp("20250101_101010")
    assert value == "20250101_101010"


def test_validate_timestamp_raises():
    wrong_timestamp = "20250101101010"
    with pytest.raises(argparse.ArgumentTypeError):
        validate_timestamp(wrong_timestamp)


def test_parser_same_source_and_destination_error(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parser(
            [
                "backup",
                "--source",
                "fake/path",
                "--destination",
                "fake/path",
                "--include",
                "project1",
                "--exclude",
                "project2",
            ]
        )

    assert excinfo.value.code == 2

    captured = capsys.readouterr()
    assert "Source and destination can't be the same directory." in captured.err


def test_parser_include_exclude_error(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parser(
            [
                "backup",
                "--source",
                "fake/path",
                "--destination",
                "out/path",
                "--include",
                "project1",
                "--exclude",
                "project2",
            ]
        )

    assert excinfo.value.code == 2

    captured = capsys.readouterr()
    assert (
        "You cannot use both --include and --exclude at the same time." in captured.err
    )


def test_parser_invalid_source_dir(capsys):
    with pytest.raises(SystemExit) as excinfo:
        parser(["backup", "--source", "fake/path", "--destination", "out/path"])

    assert excinfo.value.code == 2

    captured = capsys.readouterr()
    assert "Source directory does not exists" in captured.err


def test_parser_invalid_destination_dir(capsys, tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        parser(["backup", "--source", str(tmp_path), "--destination", "out/path"])

    assert excinfo.value.code == 2

    captured = capsys.readouterr()
    assert "Destination directory does not exists" in captured.err


def test_parser_included_not_found(capsys, tmp_path):
    source = tmp_path / "source"
    destination = tmp_path / "destination"

    source.mkdir()
    destination.mkdir()

    with pytest.raises(SystemExit) as excinfo:
        parser(
            [
                "backup",
                "--source",
                str(source),
                "--destination",
                str(destination),
                "--include",
                "project1",
            ]
        )

    assert excinfo.value.code == 2

    captured = capsys.readouterr()
    assert "Included project(s) not found in" in captured.err


def test_parser_returns_cli_arguments(capsys, tmp_path):
    source = tmp_path / "source"
    destination = tmp_path / "destination"

    source.mkdir()
    destination.mkdir()

    result = parser(
        [
            "backup",
            "--source",
            str(source),
            "--destination",
            str(destination),
        ]
    )

    assert isinstance(result, CliArguments)
    assert result.command == "backup"
    assert result.source == source
    assert result.destination == destination
