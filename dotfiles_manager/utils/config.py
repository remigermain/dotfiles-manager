import hashlib
import json
import os
import shutil
from functools import wraps
from pathlib import Path
from typing import Any

from .encoder import JsonEncoder
from .expection import ConfigError
from .shell import run
from .singleton import Singleton

DOTFILE_RC = Path("~/.dotfilerc").expanduser()
USER = os.getenv("HOME") + "/"
DEFAULT_PROFILE = "base"


class FsScope:
    def __init__(self, base, name):
        self.base = base
        self.name = name

    def _sanitize_path(self, path) -> [Path, bool]:
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

    def is_system_path(self, path) -> bool:
        return not str(Path(path).expanduser()).startswith(USER)

    def chmod(self, source, mod):
        run(["chmod", oct(mod).replace("0o", ""), str(source)])

    def is_dir(self, source):
        r = run([f'[ -d "{source}" ] && echo true || echo false']).stdout.lower().strip()
        return r == "true"

    def copy(self, source, dest):
        source = Path(source)
        dest = Path(dest)
        self.mkdir(dest.parent)
        self.remove(dest)
        run(["cp", "-rf", str(source), str(dest)])

    def link(self, source, dest) -> bool:
        source = Path(source).expanduser()
        dest = Path(dest).expanduser()

        if dest.resolve() == source:
            return False

        self.mkdir(dest.parent)
        self.remove(dest)
        run(["ln", "-s", str(source), str(dest)])
        return True

    def remove(self, source: Path):
        """source is host"""
        source = Path(source).expanduser()
        # if self.exist(source):
        run(["rm", "-rf", str(source)])

    def exist(self, source) -> bool:
        r = run([f'[ -e "{source}" ] && echo true || echo false']).stdout.lower().strip()
        return r == "true"

    def stat(self, source) -> os.stat_result:
        return Path(source).stat()

    def md5sum(self, source):
        try:
            with open(source, "rb") as f:
                h = hashlib.new("md5")
                for chunk in iter(lambda: f.read(128 * h.block_size), b""):
                    h.update(chunk)
                return h.hexdigest()
        except FileNotFoundError:
            return None

    def mkdir(self, path):
        run(["mkdir", "-p", str(path)])

    # --- local ---
    def lbase(self, path):
        return Path(self.base / path)

    def ldata(self, path):
        return Path(Path(self.name) / path)

    def lpath(self, path) -> Path:
        """convert path to local dotfile path"""
        return self.lbase(self.ldata(path))

    @wraps(Path.open)
    def lopen(self, filename, *ar, **kw):
        return self.open(self.lpath(filename))

    @wraps(shutil.copy2)
    def lcopy(self, source, dest, *ar, **kw):
        return self.copy(self.lpath(source), dest, *ar, **kw)

    def llink(self, source, dest):
        """dest is host destination"""
        return self.link(self.lpath(source), dest)

    def lstat(self, source) -> os.stat_result:
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
        self.remove(self.lpath(source))

    def lexist(self, source) -> bool:
        path, _ = self._sanitize_path(source)
        return self.exist(self.lpath(path))

    def lmd5sum(self, source) -> str:
        return self.md5sum(self.lpath(source))

    def lmkdir(self, path):
        self.mkdir(self.lpath(path))


class ConfigScope:
    def __init__(self, name, config):
        self.name = name
        self._config = config
        self._local_config = config.setdefault(self.name, {})
        self._base = config.path
        self.fs = FsScope(self._base, self.name)

    @property
    def path(self):
        return self.fs.lpath("")

    def get(self, key, *ar) -> Any:
        if key not in self._local_config:
            if not ar:
                return KeyError(key)
            return ar[0]

        return self._local_config[key]

    def set(self, key, content):
        self._local_config[key] = content
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
            data = data | json.loads(self._path.read_text())
        self.fs = FsScope(self._path, "")
        super().__init__(data)
        self.path.mkdir(exist_ok=True, parents=True)

    @property
    def path(self) -> Path:
        return (Path(self._path.parent) / self["data"]).expanduser()

    def save(self):
        self._path.write_text(json.dumps(self, indent=4, cls=JsonEncoder))

    def scope(self, name) -> ConfigScope:
        return ConfigScope(name, self)


class DotConfigRc(dict, metaclass=Singleton):
    def __init__(self):
        self._path = DOTFILE_RC
        data = {"profile": DEFAULT_PROFILE, "profiles": {}}
        if self._path.exists():
            data = data | json.loads(self._path.read_text() + "\n")
        super().__init__(data)
        self.fs = FsScope("", "")

    @property
    def path(self) -> Path:
        return Path(self._path).expanduser()

    def save(self):
        self.path.write_text(json.dumps(self, indent=4, cls=JsonEncoder))
        self.path.chmod(0o664)

    @property
    def dataprofile(self) -> Config:
        profile = self["profile"]
        if not profile or profile not in self["profiles"]:
            raise ConfigError("profile not select...")

        return Config(self["profiles"][profile]["directory"])

    @property
    def configprofile(self) -> dict:
        return self["profiles"].get(self["profile"], {})


def rc_exists():
    return DOTFILE_RC.exists()


def config_exists():
    if not DOTFILE_RC.exists():
        return False

    try:
        _ = DotConfigRc().dataprofile
    except ConfigError:
        return False
    else:
        return True
