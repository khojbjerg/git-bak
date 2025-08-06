from git_bak.exceptions import RunnerError
from git_bak.runners import CommandRunner


class FakeRunner(CommandRunner):
    def __init__(self, fail_on: str | None):
        self._fail_on = fail_on

    def run(self, cmd: list[str]) -> None:
        cmd_str = " ".join(cmd)
        if self._fail_on and self._fail_on in cmd_str:
            raise RunnerError("FakeRunner exception")
        return None
