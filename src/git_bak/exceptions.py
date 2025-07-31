class GitBakException(Exception):
    pass


class BackupError(GitBakException):
    pass


class RestoreError(GitBakException):
    pass


class CommandError(GitBakException):
    pass


class GitRepoInvalid(GitBakException):
    pass


class GitRepoHasNoCommits(GitBakException):
    pass
