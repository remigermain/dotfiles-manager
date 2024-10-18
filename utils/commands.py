import importlib
import inspect
from pathlib import Path

from commands.base import CommandAbstract, SubCommandAbstract

BASE = Path(__file__).parent.parent


def list_commands():
    for path in BASE.glob("commands/*.py"):
        basename = path.name
        dirname = path.parent.name
        module_name = f"{dirname}.{basename.split(".")[0]}"

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
