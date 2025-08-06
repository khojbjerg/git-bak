import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass

from git_bak.exceptions import RunnerError


@dataclass
class RunnerResult:
    cmd: list[str]
    returncode: int
    msg: str


class CommandRunner(ABC):
    @abstractmethod
    def run(self, cmd: list[str]) -> RunnerResult:  # pragma: no cover
        raise NotImplementedError


class SubprocessRunner(CommandRunner):
    def run(self, cmd: list[str]) -> RunnerResult:
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return RunnerResult(
                cmd=" ".join(cmd),
                returncode=result.returncode,
                msg=result.stderr if result.stderr else result.stdout,
            )
        except subprocess.CalledProcessError as e:
            raise RunnerError(str(e.stderr).strip()) from e
