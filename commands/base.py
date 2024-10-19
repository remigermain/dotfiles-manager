import abc
import argparse
import inspect
import sys

from utils.conf import ConfigScope
from utils.logger import Logger, Style


class CommandAbstract(metaclass=abc.ABCMeta):
    help = None

    def __init__(self, config=None):
        if not hasattr(self, "name"):
            self.name = type(self).__name__.lower()

        self.stdout = Logger(sys.stdout)
        self.stderr = Logger(sys.stderr)
        self.style = Style()

    def add_arguments(self, parser: argparse.ArgumentParser):
        return parser

    @abc.abstractmethod
    def handle(self, config, *ar, **options):
        raise NotImplementedError("You need to implement handle()")


class SubCommandAbstract(CommandAbstract):
    def add_arguments(self, parser):
        # get only modules defined
        def predicate(symbol):
            if not inspect.isclass(symbol) or not issubclass(symbol, CommandAbstract) or symbol is type(self):
                return False
            return True

        subparsers = parser.add_subparsers(description="Available commands", dest=f"{self.name}_command", required=True)
        self.__corespond = {}
        for _, subcmd in inspect.getmembers(self, predicate=predicate):
            subcmd_cls = subcmd()
            self.__corespond[subcmd_cls.name] = subcmd_cls
            command_parser = subparsers.add_parser(subcmd_cls.name, help=subcmd_cls.help)
            subcmd_cls.add_arguments(command_parser)

    def handle(self, **option):
        return self.__corespond[option[f"{self.name}_command"]].handle(**option)
