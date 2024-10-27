import abc
import argparse
import inspect
import sys
from functools import partial, wraps
from typing import Optional

from dotfiles_manager.utils.commands import COMMAND_CONFIG, init_commands
from dotfiles_manager.utils.config import ConfigScope, DotConfigRc
from dotfiles_manager.utils.logger import Logger, Style


class CommandType(abc.ABCMeta):
    def __new__(cls, name, base, namespace):
        namespace.setdefault("name", name.lower().removeprefix("command"))
        namespace.setdefault("abstract", False)
        namespace.setdefault(COMMAND_CONFIG, {"rc": True, "config": True})
        return super().__new__(cls, name, base, namespace)


class CommandAbstract(metaclass=CommandType):
    help = None
    abstract = True
    aliases = ()
    parent = None

    def __init__(self, config=None, parent=None):
        self.style = Style()
        self.stdout = Logger(sys.stdout, self.style)
        self.stderr = Logger(sys.stderr, self.style)
        self._parent = parent or self.parent

    @property
    def rc(self) -> DotConfigRc:
        return DotConfigRc()

    @property
    def profil(self) -> dict:
        return self.rc["profiles"][self.rc["profile"]]

    @property
    def config(self) -> ConfigScope:
        scopename = self.name
        if self._parent:
            if issubclass(type(self._parent), (CommandAbstract, SubCommandAbstract)):
                scopename = self._parent.name
            else:
                scopename = self._parent
        return self.rc.dataprofile.scope(scopename)

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add command arguments"""

    def subcommands(self):
        raise NotImplementedError("You need to implement subcommands()")

    @abc.abstractmethod
    def handle(self, **options) -> Optional[int]:
        raise NotImplementedError("You need to implement handle()")


def command(func=None, /, name=None, help=None, aliases=None):
    if func is None:
        return partial(command, name=name, help=help, aliases=aliases)

    class CommandWrapppers(CommandAbstract):
        def __init__(self, parent):
            self.name = name or func.__name__
            self.help = help
            self.aliases = aliases or ()
            super().__init__(parent=parent)

            @wraps(func)
            def _wrap(*ar, **kw):
                return self.handle(*ar, **kw)

            setattr(parent, func.__name__, _wrap)

        @wraps(func)
        def handle(self, *ar, **kw):
            return func(self._parent, *ar, **kw)

    return CommandWrapppers


class SubCommandAbstract(CommandAbstract):
    abstract = True

    def subcommands(self):
        return self._coresponds

    def add_arguments(self, parser: argparse.ArgumentParser):
        # get only modules defined
        def predicate(symbol):
            if not inspect.isclass(symbol) or not issubclass(symbol, CommandAbstract) or symbol is type(self):
                return False

            return True

        subparsers = parser.add_subparsers(
            description="Available commands", dest=f"SUBCOMMAND_{self.name}_command", required=True
        )
        parent = self._parent or self
        self._coresponds = init_commands(
            [subcmd for _, subcmd in inspect.getmembers(type(self), predicate=predicate)], subparsers, parent=parent
        )

    def handle(self, **option) -> Optional[int]:
        cmd, _ = self._coresponds[option[f"SUBCOMMAND_{self.name}_command"]]
        return cmd.handle(**option)
