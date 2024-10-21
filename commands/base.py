import abc
import argparse
import inspect
import sys
from typing import Optional

from utils.commands import init_commands
from utils.config import ConfigScope, DotConfigRc
from utils.logger import Logger, Style


class CommandType(abc.ABCMeta):
    def __new__(cls, name, base, namespace):
        namespace.setdefault("name", name.lower().removeprefix("command"))
        namespace.setdefault("abstract", False)
        return super().__new__(cls, name, base, namespace)


class CommandAbstract(metaclass=CommandType):
    help = None
    abstract = True
    aliases = ()

    def __init__(self, config=None, parent=None):
        self.style = Style()
        self.stdout = Logger(sys.stdout, self.style)
        self.stderr = Logger(sys.stderr, self.style)
        self._parent = parent

    @property
    def rc(self) -> DotConfigRc:
        return DotConfigRc()

    @property
    def profil(self) -> dict:
        return self.rc["profiles"][self.rc["profile"]]

    @property
    def config(self) -> ConfigScope:
        return self.rc.dataprofile.scope(self._parent.name if self._parent else self.name)

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add command arguments"""

    @abc.abstractmethod
    def handle(self, **options) -> Optional[int]:
        raise NotImplementedError("You need to implement handle()")


class SubCommandAbstract(CommandAbstract):
    abstract = True

    def add_arguments(self, parser: argparse.ArgumentParser):
        # get only modules defined
        def predicate(symbol):
            if not inspect.isclass(symbol) or not issubclass(symbol, CommandAbstract) or symbol is type(self):
                return False
            return True

        subparsers = parser.add_subparsers(description="Available commands", dest=f"{self.name}_command", required=True)
        self.__coresponds = init_commands(
            [subcmd for _, subcmd in inspect.getmembers(self, predicate=predicate)], subparsers, parent=self
        )

    def handle(self, **option) -> Optional[int]:
        cmd, _ = self.__coresponds[option[f"{self.name}_command"]]
        return cmd.handle(**option)
