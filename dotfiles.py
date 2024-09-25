import argparse
import glob
import importlib.util
import inspect
import json
import logging
import os
import sys
from pathlib import Path

from commands.base import CommandAbstract
from utils.utils import DictProxy

try:
    from functools import cache
except Exception:
    from functools import lru_cache

    cache = lru_cache()


BASE = os.path.dirname(os.path.abspath(__file__))

logging.addLevelName(100, "APP")


def save_config(config):
    logger.info("Save settings...")
    with config.DOTFILES_CONFIG_PATH.open("w") as f:
        del config.DOTFILES_CONFIG_PATH
        del config.DOTFILES_DATA_PATH
        json.dump(config, f, default=str, indent=4)


CONFIG = None


@cache
def get_config(config, base_path):
    if not config:
        config = Path("~/.dotfilesmanager").expanduser().resolve()

        if not config.exists():
            raise ValueError("not configurated dotefiles manager exists not exists.")

        with config.open() as f:
            value = f.read().strip()

        if not value:
            raise ValueError(f"files {config!r} are empty.")

        config = value

    config = Path(value).expanduser().resolve()
    if not config.exists():
        raise ValueError(f"file {config} not exists.")

    with config.open() as f:
        config_content = DictProxy(json.load(f))

    if base_path:
        base_path = Path(base_path).expanduser().resolve()
    else:
        base_path = config.parent

    if not base_path.exists():
        raise ValueError(f"data folders {base_path!r} not exists.")

    config_content["DOTFILES_CONFIG_PATH"] = config
    config_content["DOTFILES_DATA_PATH"] = base_path

    global CONFIG
    CONFIG = config_content

    config_content.setdefault("linked", [])
    config_content.setdefault("copies", [])
    config_content.setdefault("config", [])

    return config_content, base_path


# base logger
class DeployLogger(logging.Logger):
    verbose_enable = False

    def show(self, *ar, **kw):
        self.log(100, *ar, **kw)


logger = DeployLogger("deploy", level=100)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def commands():
    for path in glob.glob(f"{os.path.join(BASE, "commands")}/*.py"):
        basename = os.path.basename(path)
        dirname = os.path.basename(os.path.dirname(path))
        module_name = f"{dirname}.{basename.split(".")[0]}"

        # import modules from basename
        module = importlib.import_module(module_name)

        # get only modules defined
        def predicate(symbol, module_name=module_name):
            if (
                not inspect.isclass(symbol)
                or symbol is CommandAbstract
                or symbol.__module__ != module_name
                or not issubclass(symbol, CommandAbstract)
            ):
                return False
            return True

        for _, clss in inspect.getmembers(module, predicate=predicate):
            yield clss


def main(arguments, _sub="sub"):
    parser = argparse.ArgumentParser("dotfiles manager")

    parser.add_argument("-v", "--verbose", action="store_true", help="Show deploy verbose")
    parser.add_argument(
        "--verbose-level",
        default=logging.INFO,
        help="Change verbose level",
        choices=list(logging._levelToName.values()),
    )
    parser.add_argument("-c", "--config", default=None, help="Select config files")

    parser.add_argument("--base-path", default=None, help="Base path where files are stocked.")

    subparsers = parser.add_subparsers(description="Available commands", dest="command", required=True)

    corespond = {}

    for command in commands():
        logger.debug(f"Avaialable {command=}")

        command_cls = command(logger, main)
        corespond[command_cls.name] = command_cls
        command_parser = subparsers.add_parser(command_cls.name, help=command_cls.description)

        logger.debug(f"Add arguments for {command_cls.name!r}")
        command_cls.add_arguments(command_parser)

    flags = parser.parse_args(arguments)
    if flags.verbose:
        logger.setLevel(flags.verbose_level)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))

    config, base = get_config(flags.config, flags.base_path)

    logger.debug(f"{config=} {base=}")

    logger.info(f"Run {_sub}command {flags.command!r}")
    results = corespond[flags.command].pre_run(config, base, flags)
    if results is not None:
        config, base, flags = results
    corespond[flags.command].run(config, base, flags)


if __name__ == "__main__":
    main(sys.argv[1:], _sub="")
    save_config(CONFIG)
