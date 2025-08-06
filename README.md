# git-bak

`git-bak` is a simple CLI tool designed for automated backup and restore of local Git repositories. It allows you to easily mirror your repositories to another location and restore them when needed.

## Features

- 🔄 Backup and restore local Git repositories.
- 🎯 Filter repositories using `--include` and `--exclude`.
- 🕒 Restore from the latest or a specific timestamped backup.
- 🧾 Optional file and console logging.
- 🤫 Quiet mode for background jobs (e.g., cron).

## Installation

```bash
pip install git-bak
```

## Usage

### Backup

```bash
git-bak backup --source /path/to/repos --destination /path/to/backup [options]
```

### Restore

```bash
git-bak restore --source /path/to/backup --destination /path/to/restore [options]
```

### Parameters

| Parameter        | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `--source`       | Path to the source directory (where the repos are located or backed up).   |
| `--destination`  | Path to the destination directory (where to store or restore repositories). |
| `--include`      | *(Optional)* List of repository names to include. Seperate names by space.                           |
| `--exclude`      | *(Optional)* List of repository names to exclude. Seperate names by space.                           |                           |
| `--timestamp`    | *(Optional)*, Restore from a specific backup timestamp (e.g 20250731_1000). If not provided, restores the latest backup. |
| `--verbose`       | *(Optional)* Enable debug logging.                              |
| `--log-to-file`       | *(Optional)* Enable file logging. Log file location: $HOME/git_backup|restore.log                              |
| `--quiet`       | *(Optional)* Suppress console output (StreamHandler) (useful for cron)..    


If neither `--include` nor `--exclude` are specified, all repositories in the source directory will be backed up or restored.


## Logging

- Log level defaults to `INFO`. Use `--verbose` to increase to `DEBUG`.
- Use `--quiet` to silence all console output.
- File logging is **disabled by default**. Enable it with `--log-to-file`.
  - Backup logs go to: `$HOME/git_backup.log`
  - Restore logs go to: `$HOME/git_restore.log`

## Examples

Backup all repositories:

```bash
git-bak backup --source ~/projects --destination ~/git_backups
```

Backup only selected repositories with debug logs printed:

```bash
git-bak backup --source ~/projects --destination ~/git_backups --include repo1 repo2 --verbose
```

Backup all repositories quietly in a cron job:

```bash
git-bak backup --source ~/projects --destination ~/git_backups --quiet --log-to-file
```

Restore the latest backup of all repositories:

```bash
git-bak restore --source ~/git_backups --destination ~/restored_projects
```

Restore a specific backup from a timestamp:

```bash
git-bak restore --source ~/git_backups --destination ~/restored_projects --timestamp 20250731_150000
```