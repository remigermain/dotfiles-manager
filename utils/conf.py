import hashlib
import os
import shutil
from functools import wraps
from pathlib import Path

USER = os.getenv("HOME") + "/"
from .config import DotfileRC


class NotSet: ...


NOSET = NotSet()


class FsScope:
    def __init__(self, base):
        self.base = base

    def _sanitize_path(self, path):
        path = Path(path).expanduser()
        if not self.is_system_path(path):
            path = Path(str(path).removeprefix(USER))
            prefix = "user"
            is_user = True
        else:
            prefix = "system"
            is_user = False

        path = Path(str(path).removeprefix("/"))
        return prefix / path, is_user

    def is_system_path(self, path):
        return not str(Path(path).expanduser()).startswith(USER)

    @wraps(Path.open)
    def open(self, filename, *ar, **kw):
        return Path(filename).open(*ar, **kw)

    @wraps(shutil.copy2)
    def copy(self, source, dest):
        self.remove(dest)
        if source.is_dir():
            return shutil.copytree(source, dest)
        else:
            return shutil.copy2(source, dest, follow_symlinks=False)

    def link(self, source, dest):
        source = Path(self.base / source)
        dest = Path(dest).expanduser()

        if dest.resolve() == source:
            return False

        self.remove(dest)
        dest.symlink_to(source)
        return True

    def remove(self, source: Path):
        """source is host"""
        source = Path(source).expanduser()
        if source.exists():
            if source.is_dir() and not source.is_symlink():
                shutil.rmtree(source)
            else:
                source.unlink()
            return True
        return False

    @wraps(Path.exists)
    def exist(self, source):
        return Path(source).exists()

    def stat(self, source):
        return Path(source).stat()

    def md5sum(self, source):
        h = hashlib.new("md5")
        with open(source, "rb") as f:
            for chunk in iter(lambda: f.read(128 * h.block_size), b""):
                h.update(chunk)
        return h.hexdigest()

    # --- local ---

    def lpath(self, path) -> Path:
        """convert path to local dotfile path"""
        return self.base / path

    @wraps(Path.open)
    def lopen(self, filename, *ar, **kw):
        return self.open(self.base / filename)

    @wraps(shutil.copy2)
    def lcopy(self, source, dest, *ar, **kw):
        return self.copy(Path(self.base / source), dest, *ar, **kw)

    def llink(self, source, dest):
        """dest is host destination"""
        return self.link(self.base / source, dest)

    def lstat(self, source):
        return Path(self.base / source).stat()

    def save(self, source):
        """source is host file"""
        source = Path(source).expanduser()
        destfile, is_user = self._sanitize_path(source)

        destpath = self.base / destfile
        destpath.parent.mkdir(parents=True, exist_ok=True)
        self.copy(source, destpath)

        return destfile, is_user

    def lremove(self, source):
        """source is local"""
        return self.remove(self.base / source)

    @wraps(Path.exists)
    def lexist(self, source):
        path, _ = self._sanitize_path(source)
        return self.exist(self.base / path)

    def lmd5sum(self, source):
        return self.md5sum(self.base / source)


class ConfigScope:
    def __init__(self, name, config):
        self.name = name
        self._config = config
        self._local_config = config.setdefault(self.name, {})
        self._base = config.path_data
        self.fs = FsScope(self._base)

    def get(self, key, default=NOSET):
        if key not in self._local_config:
            if default is NOSET:
                return KeyError(key)
            return default

        return self._local_config[key]

    def set(self, key, content, **tags):
        self._local_config[key] = content
        self.save()

    def add(self, key, content, **tags):
        item = self._local_config.setdefault(key, [])
        item.append(content)
        self.save()

    def save(self):
        self._config.save()

    @classmethod
    def from_name(cls, name):
        config = DotfileRC.Data()
        return cls(name, config)
