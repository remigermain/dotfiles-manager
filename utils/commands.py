import importlib
import inspect
from pathlib import Path

from commands.base import CommandAbstract, SubCommandAbstract

BASE = Path(__file__).parent.parent


def generate_path(path):
    module = [path.name.split(".")[0]]
    path = path.parent
    while BASE != path:
        module.insert(0, path.name)
        path = path.parent
    return ".".join(module)


def list_commands():
    for path in BASE.glob("commands/**/*.py"):
        module_name = generate_path(path)
        # import modules from basename
        module = importlib.import_module(module_name)

        # get only modules defined
        def predicate(symbol, module_name=module_name):
            if (
                not inspect.isclass(symbol)
                or symbol in [CommandAbstract, SubCommandAbstract]
                or symbol.__module__ != module_name
                or not issubclass(symbol, CommandAbstract)
            ):
                return False
            return True

        for _, clss in inspect.getmembers(module, predicate=predicate):
            yield clss
