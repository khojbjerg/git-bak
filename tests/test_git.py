import pytest

from git_bak.exceptions import GitBundleError, GitRepoHasNoCommits, GitRepoInvalid


def test_assert_valid_repo(make_git) -> None:
    git = make_git(fail_on=None)
    git.assert_valid_repo("/fake/path")


def test_assert_valid_repo_raises(make_git) -> None:
    git = make_git(fail_on="rev-parse --is-inside-work-tree")
    with pytest.raises(GitRepoInvalid):
        git.assert_valid_repo("/failing/fakepath")


def test_assert_has_commits(make_git):
    git = make_git(fail_on=None)
    git.assert_has_commits("/fake/path")


def test_assert_has_commits_raises(make_git):
    git = make_git(fail_on="rev-parse --verify")
    with pytest.raises(GitRepoHasNoCommits):
        git.assert_has_commits("/fake/path")


def test_assert_valid_bundle(make_git):
    git = make_git(fail_on=None)
    git.assert_valid_bundle("/fake/path")


def test_assert_valid_bundle_raises(make_git):
    git = make_git(fail_on="bundle verify")
    with pytest.raises(GitRepoInvalid):
        git.assert_valid_bundle("/fake/path")


def test_create_bundle(tmp_path, mock_now, make_git):
    git = make_git(fail_on=None)

    source = tmp_path / "source" / "project1"
    destination = tmp_path / "destination"

    source.mkdir(parents=True)
    destination.mkdir()

    result = git.create_bundle(source, destination)
    assert result == str(destination / "project1" / "project1.bundle.20250101_101010")


def test_create_bundle_raises(tmp_path, mock_now, make_git):
    git = make_git(fail_on="bundle create")

    source = tmp_path / "source" / "project1"
    destination = tmp_path / "destination"

    source.mkdir(parents=True)
    destination.mkdir()

    with pytest.raises(GitBundleError):
        git.create_bundle(source, destination)


def test_clone_bundle(tmp_path, make_git):
    git = make_git(fail_on=None)

    source = tmp_path / "source" / "project1"
    destination = tmp_path / "destination"

    source.mkdir(parents=True)
    destination.mkdir()

    result = git.clone_bundle(source, destination)
    assert result == str(tmp_path / "destination" / "project1")


def test_clone_bundle_raises(tmp_path, make_git):
    git = make_git(fail_on="git clone")

    source = tmp_path / "source" / "project1"
    destination = tmp_path / "destination"

    source.mkdir(parents=True)
    destination.mkdir()

    with pytest.raises(GitBundleError):
        git.clone_bundle(source, destination)
