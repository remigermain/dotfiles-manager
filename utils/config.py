import hashlib
import json
import os
import shutil
import subprocess
from functools import wraps
from pathlib import Path
from tempfile import NamedTemporaryFile

from .encoder import JsonEncoder
from .expection import ConfigError
from .singleton import Singleton

DOTFILE_RC = "/etc/.dotfilerc.json"

USER = os.getenv("HOME") + "/"


class NotSet: ...


NOSET = NotSet()


def run(cmds):
    res = subprocess.run(cmds, capture_output=True)
    if res.returncode == 0:
        return

    err = res.stderr.decode()
    if "permission denied" in err.lower():
        cmds = ["sudo", *cmds]
        res = subprocess.run(cmds, capture_output=True)

        if res.returncode == 0:
            return
        err = res.stderr.decode()
    raise ValueError(err)


class FsScope:
    def __init__(self, base, name):
        self.base = base
        self.name = name

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
        source = Path(source)
        dest = Path(dest)
        # self.remove(dest)
        self.mkdir(dest.parent)
        if source.is_dir():
            run(["cp", "-r", str(source), str(dest)])
            # return shutil.copytree(source, dest)
        else:
            run(["cp", str(source), str(dest)])
            # return shutil.copy2(source, dest, follow_symlinks=False)

    def link(self, source, dest):
        source = Path(self.lpath(source))
        dest = Path(dest).expanduser()

        if dest.resolve() == source:
            return False

        self.remove(dest)
        run(["ln", "-s", str(source), str(dest)])
        # dest.symlink_to(source)
        return True

    def remove(self, source: Path):
        """source is host"""
        source = Path(source).expanduser()
        if source.exists():
            run(["rm", "-rf", str(source)])
            # if source.is_dir() and not source.is_symlink():
            #     shutil.rmtree(source)
            # else:
            #     source.unlink()
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

    def mkdir(self, path):
        run(["mkdir", "-p", str(path)])
        # Path(path).mkdir(exist_ok=True, parents=True)

    # --- local ---
    def ldata(self, path):
        return Path(Path(self.name) / path)

    def lpath(self, path) -> Path:
        """convert path to local dotfile path"""
        return Path(self.base / self.ldata(path))

    @wraps(Path.open)
    def lopen(self, filename, *ar, **kw):
        return self.open(self.lpath(filename))

    @wraps(shutil.copy2)
    def lcopy(self, source, dest, *ar, **kw):
        return self.copy(self.lpath(source), dest, *ar, **kw)

    def llink(self, source, dest):
        """dest is host destination"""
        return self.link(self.lpath(source), dest)

    def lstat(self, source):
        return self.stat(self.lpath(source))

    def save(self, source):
        """source is host file"""
        source = Path(source).expanduser()
        destfile, is_user = self._sanitize_path(source)

        destpath = self.lpath(destfile)
        self.lmkdir(destpath.parent)
        self.copy(source, destpath)

        return destfile, is_user

    def lremove(self, source):
        """source is local"""
        return self.remove(self.lpath(source))

    @wraps(Path.exists)
    def lexist(self, source):
        path, _ = self._sanitize_path(source)
        return self.exist(self.lpath(path))

    def lmd5sum(self, source):
        return self.md5sum(self.lpath(source))

    def lmkdir(self, path):
        return self.mkdir(self.lpath(path))


class ConfigScope:
    def __init__(self, name, config):
        self.name = name
        self._config = config
        self._local_config = config.setdefault(self.name, {})
        self._base = config.path
        self.fs = FsScope(self._base, self.name)

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

    def all(self):
        return self._local_config


class Config(dict):
    def __init__(self, path):
        self._path = Path(path).expanduser().resolve()
        data = {"data": "./data"}
        if self._path.exists():
            data = json.loads(self._path.read_text())
        self.fs = FsScope(self._path, "")
        super().__init__(data)

    @property
    def path(self):
        return (Path(self._path.parent) / self["data"]).expanduser()

    def save(self):
        with NamedTemporaryFile() as f:
            f.write(json.dumps(self, indent=4, cls=JsonEncoder).encode())
            f.seek(0)
            self.fs.copy(f.name, self._path)

        # self._path.write_text(json.dumps(self, indent=4, cls=JsonEncoder))

    def scope(self, name):
        return ConfigScope(name, self)


class DotConfigRc(dict, metaclass=Singleton):
    def __init__(self):
        self._path = Path(DOTFILE_RC).expanduser()
        data = {"profile": "base", "profiles": {}}
        if self._path.exists():
            data = json.loads(self._path.read_text())
        super().__init__(data)
        self.fs = FsScope("", "")

    def save(self):
        with NamedTemporaryFile() as f:
            f.write(json.dumps(self, indent=4, cls=JsonEncoder).encode())
            f.seek(0)
            self.fs.copy(f.name, self._path)

    @property
    def dataprofile(self):
        profile = self["profile"]
        if not profile or profile not in self["profiles"]:
            raise ConfigError("profile not select...")

        return Config(self["profiles"][profile]["directory"])

    @property
    def configprofile(self):
        return self["profiles"].setdefault(self["profile"], {})
