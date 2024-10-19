#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from utils.commands import list_commands
from utils.expection import ConfigError

try:
    from functools import cache
except Exception:
    from functools import lru_cache

    cache = lru_cache()


BASE = os.path.dirname(os.path.abspath(__file__))


def save_config(config):
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
        config_content = json.load(f)

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


def parse_tags(lst):
    obj = {}
    for value in lst or []:
        k, value = value.split("=")
        obj[k] = value
    return obj


def main(arguments, _sub="sub") -> Optional[int]:
    parser = argparse.ArgumentParser("dotfiles manager")

    parser.add_argument("-c", "--config", default=None, help="Select config files")
    parser.add_argument("--base-path", default=None, help="Base path where files are stocked.")
    parser.add_argument("--tags", nargs="?", help="add tags to acitons")

    subparsers = parser.add_subparsers(description="Available commands", dest="command", required=True)

    corespond = {}

    for command in list_commands():
        command_cls = command()
        corespond[command_cls.name] = command_cls
        command_parser = subparsers.add_parser(command_cls.name, help=command_cls.help)

        command_cls.add_arguments(command_parser)

    options = vars(parser.parse_args(arguments))
    options["tags"] = parse_tags(options.get("tags", []))

    try:
        return corespond[options["command"]].handle(**options)
    except KeyboardInterrupt:
        return 100
    except ConfigError as e:
        print(str(e))
        return 101


if __name__ == "__main__":
    exit(main(sys.argv[1:], _sub=""))
