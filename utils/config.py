import contextlib
import json
import os
import shutil
from pathlib import Path

from .expection import ConfigError


class DictSave(dict):
    def __init__(self, path, data):
        self._path = path
        super().__init__(data)

    def save(self):
        self._path.write_text(json.dumps(self, indent=4))


class Copp:
    def __init__(self, base, prefix):
        self._base = Path(base)
        self._prefix = Path(prefix)

    def save(self, element):
        element = Path(element)
        if str(element).startswith(os.getenv("HOME")):
            dest = "home/__dotfiles__/" / Path(str(element).removeprefix(os.getenv("HOME") + "/"))
        else:
            dest = Path(element)

        output = self._base / self._prefix
        (output / dest.parent).mkdir(exist_ok=True, parents=True)

        shutil.copy2(element, output / dest)
        return dest

    def link(self, source, dest):
        source = Path(source)
        dest = Path(dest)

        output = self._base / self._prefix / source
        dest.unlink(missing_ok=True)

        dest.symlink_to(Path(output).expanduser())
        return dest

    def copyfile(self, source, dest):
        dest = Path(dest).expanduser()
        dest.unlink()
        shutil.copy2((self._base / self._prefix / source), dest)

    def delete(self, source):
        (self._base / self._prefix / source).unlink()


class DotfileData(DictSave):
    def __init__(self, path):
        path = Path(path).expanduser().resolve()
        data = {"data": "./data"}
        if path.exists():
            data = json.loads(path.read_text())
        super().__init__(path, data)

    @contextlib.contextmanager
    def files(self, prefix):
        yield Copp(Path(self._path.parent) / Path(self["data"]), prefix)


class DotfileRC(DictSave):
    def __init__(self):
        path = Path("~/.dotfilerc.json").expanduser()
        data = {"profile": "base", "profiles": {}}
        if path.exists():
            data = json.loads(path.read_text())
        super().__init__(path, data)

    @classmethod
    def Data(cls) -> DotfileData:
        rc = cls()
        profile = rc["profile"]
        if not profile or profile not in rc["profiles"]:
            raise ConfigError("profile not select...")

        return DotfileData(rc["profiles"][profile]["directory"])
