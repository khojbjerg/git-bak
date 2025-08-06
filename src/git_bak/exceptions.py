class GitBakException(Exception):
    pass


class BackupError(GitBakException):
    pass


class RestoreError(GitBakException):
    pass


class GitError(GitBakException):
    pass


class GitRepoInvalid(GitError):
    pass


class GitRepoHasNoCommits(GitError):
    pass


class GitBundleError(GitError):
    pass


class RunnerError(GitBakException):
    pass
