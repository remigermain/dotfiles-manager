import argparse
import importlib
import importlib.util
import inspect
from functools import partial
from pathlib import Path
from typing import ForwardRef, Union

from .config import config_exists, rc_exists

BASE = Path(__file__).parent.parent



satus_rc_exists = rc_exists()
status_config_exists = config_exists()


def list_commands():
    from dotfiles_manager.commands.base import CommandAbstract

    cmds = []
    for path in BASE.glob("commands/**/*.py"):
        spec = importlib.util.spec_from_file_location("dotfiles_manager.commands", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # get only modules defined
        def predicate(symbol, module_name=module.__name__):
            if (
                not inspect.isclass(symbol)
                or symbol.__module__ != module_name
                or not issubclass(symbol, CommandAbstract)
                or symbol.abstract is True
            ):
                return False

            if has_required(symbol, "rc") and not satus_rc_exists:
                return False
            if has_required(symbol, "config") and not status_config_exists:
                return False

            return True

        for _, clss in inspect.getmembers(module, predicate=predicate):
            cmds.append(clss)

    cmds.sort(key=lambda e: e.name)

    yield from cmds


def init_commands(commands, parser, parent=None):
    corespond = {}
    for command in commands:
        command_cls = command(parent=parent)
        command_parser = parser.add_parser(command_cls.name, aliases=command_cls.aliases, help=command_cls.help)
        info = (command_cls, command_parser)
        for name in [command_cls.name, *command_cls.aliases]:
            corespond[name] = info
        command_cls.add_arguments(command_parser)

    return corespond


def parse_options(
    corresponds: dict[str, Union[ForwardRef("CommandAbstract"), argparse.ArgumentParser]],
    parser: argparse.ArgumentParser,
    arguments: list[str],
):
    options = vars(parser.parse_args(arguments))
    options["parser"] = parser
    options["list_commands"] = corresponds

    return options


COMMAND_CONFIG = "COMMAND_CONFIG"


def has_required(_cls, key):
    if not hasattr(_cls, COMMAND_CONFIG):
        return False

    return getattr(_cls, COMMAND_CONFIG).get(key, False)


def _wrap(key: str, status: bool, cls):
    getattr(cls, COMMAND_CONFIG)[key] = status
    return cls


def require_rc(status: bool):
    return partial(_wrap, "rc", status)


def require_config(status: bool):
    return partial(_wrap, "config", status)
