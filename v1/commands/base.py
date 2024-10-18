import abc
import sys
from pathlib import Path

from .extras import ALL


class Extras:
    def __init__(self, logger, *extras):
        self._dtc = {}
        for extra in extras:
            el = extra(logger, self)
            self._dtc[el.name] = el
            setattr(self, el.name, el)

    def __iter__(self):
        return iter(self._dtc.items())


class CommandAbstract(abc.ABC):
    description = None

    def __init__(self, logger, exec_command):
        self.logger = logger
        self.extras = Extras(self.logger, *ALL)
        for name, el in self.extras:
            setattr(self, name, el)

        if not hasattr(self, "name"):
            self.name = type(self).__name__.lower()

        if not hasattr(self, "directory"):
            self.directory = self.name

        if self.directory is not None:
            self.directory = Path(self.directory)
        self.exec_command = exec_command

    def pre_run(self, config, base, flags):
        if self.directory is not None:
            base = base / self.directory
            base.mkdir(exist_ok=True, parents=True)

        return config, base, flags

    def add_arguments(self, parser):
        pass

    def errx(self, *ar, **kw):
        print(*ar, **kw, file=sys.stderr)
        exit(1)

    def run(self, config, base, flags):
        raise NotImplementedError("need to implements 'run' method")

    def sanitize_path(self, path):
        return Path(str(path).replace(str(Path.home()), "~"))

    def final_path(self, path):
        return Path(path).expanduser()
