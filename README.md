# Dotfiles Manager

**Centralized management of your dotfiles, backups, symlinks, and scripts on Linux.**

This project allows you to easily manage your configuration files (dotfiles) by linking or copying them from a central repository to your system. It also supports running utility scripts to automate common tasks (backup, install, updates, etc.).

---

## 📦 Project Structure

| Path | Description |
|------|-------------|
| `~/.dotfile` | File containing the path to your dotfiles repository |
| `$DOTFILES_BASE/files/` | Directory containing files to link/copy |
| `files/home.link/` | Files to symlink in `$HOME` |
| `files/home.copy/` | Files to copy in `$HOME` |
| `files/system.link/` | Files to symlink in `/` (requires sudo) |
| `files/system.copy/` | Files to copy in `/` (requires sudo) |
| `$DOTFILES_BASE/scripts/` | Utility scripts executable via `dotfiles-manager run` |

---

## 🛠 Installation

1. **Install package**:
   ```bash
   pip install manager-dotfiles
   ```

2. **Create the `~/.dotfile` file**:
   ```bash
   echo "/path/to/your/dotfiles" > ~/.dotfile
   ```
   *Example:*
   ```bash
   echo "~/.config/dotfiles" > ~/.dotfile
   ```

---

## 🚀 Usage

### Main Commands

| Command | Description |
|---------|-------------|
| `dotfiles-manager init` | Symlink/copy all dotfiles |
| `dotfiles-manager init-link` | Symlink all dotfiles |
| `dotfiles-manager init-copy` | Copy all dotfiles |
| `dotfiles-manager link <file>` | Symlink a specific file |
| `dotfiles-manager unlink <file>` | Remove a symlink |
| `dotfiles-manager copy <file>` | Copy a specific file |
| `dotfiles-manager run <script> [args...]` | Run a utility script |

cli can be invoked by `dotfiles-manager` or `dm`, with previous command:
```bash
dm init
dm init-link
dm init-copy
dm link ~/.bashrc
dm unkink ~/.bashrc
dm copy /etc/host
dm run backup.sh
```

### Global Options

| Option | Description |
|--------|-------------|
| `-y` | Assume "yes" to all prompts |
| `-n` | Assume "no" to all prompts |
| `-v` | Verbose mode |
| `--sudo` | Run all commands with sudo |
| `-c` | Disable colored output |

---

### Examples

1. **Initialize all dotfiles**:
   ```bash
   dotfiles-manager init
   ```

2. **Symlink a specific file**:
   ```bash
   dotfiles-manager link files/home.link/.bashrc
   ```

3. **Copy a system file** (requires sudo):
   ```bash
   dotfiles-anager --sudo copy /etc/hosts
   ```

4. **Run a utility script**:
   ```bash
   dotfiles-manager run backup
   ```

---

## 📂 Structure

```bash
~/.dotfile → /path/to/dotfiles
/path/to/dotfiles/
├── files/
│   ├── home.link/
│   │   ├── .bashrc
│   │   ├── .vimrc
│   │   └── ...
│   ├── home.copy/
│   │   ├── .config/...
│   │   └── ...
│   ├── system.link/
│   │   └── etc/...
│   └── system.copy/
│       └── etc/...
└── scripts/
    ├── backup.sh
    ├── install-docker.sh
    ├── pin.py
    └── ...
```

---

## 📝 Notes

- `system.link` and `system.copy` commands can be require `sudo`.
- The `~/.dotfile` file must contain the absolute path to your repository.
- Scripts in `scripts/` must be executable (`chmod +x`) with shebang (`#!/usr/bin/env bash` or `#!/usr/bin/env python3`).

---

## 🤝 Contributing

Contributions are welcome! Open an issue or a pull request.

---

## 📄 License

MIT
