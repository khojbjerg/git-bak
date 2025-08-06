import subprocess
from unittest.mock import patch

import pytest

from git_bak.exceptions import RunnerError
from git_bak.runners import RunnerResult, SubprocessRunner


def test_subprocess_runner_run():
    runner = SubprocessRunner()
    result = runner.run(["echo", "True"])
    assert isinstance(result, RunnerResult)
    assert result.returncode == 0


@patch.object(subprocess, "run")
def test_subprocess_runner_run_raises(mock_subprocess_run):
    cmd = ["fake-command", "True"]
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=cmd, stderr="error"
    )
    runner = SubprocessRunner()

    with pytest.raises(RunnerError):
        runner.run(cmd)
