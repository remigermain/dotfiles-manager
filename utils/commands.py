import argparse
import importlib
import inspect
from pathlib import Path
from typing import ForwardRef, Union

BASE = Path(__file__).parent.parent


def generate_path(path):
    module = [path.name.split(".")[0]]
    path = path.parent
    while BASE != path:
        module.insert(0, path.name)
        path = path.parent
    return ".".join(module)


def list_commands():
    from commands.base import CommandAbstract

    cmds = []
    for path in BASE.glob("commands/**/*.py"):
        module_name = generate_path(path)
        # import modules from basename
        module = importlib.import_module(module_name)

        # get only modules defined
        def predicate(symbol, module_name=module_name):
            if (
                not inspect.isclass(symbol)
                or symbol.__module__ != module_name
                or not issubclass(symbol, CommandAbstract)
                or symbol.abstract is True
            ):
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
        corespond[command_cls.name] = command_cls, command_parser
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
