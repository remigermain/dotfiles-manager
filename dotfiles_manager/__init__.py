#!/usr/bin/env python3
import argparse
import sys
from typing import Optional

from .utils.commands import init_commands, list_commands, parse_options
from .utils.config import DotConfigRc
from .utils.logger import Style


def main(arguments) -> Optional[int]:
    parser = argparse.ArgumentParser("dotfiles manager")

    parser.add_argument("--color", action="store_true", help="active output colors", dest="color", default=None)
    parser.add_argument("--no-color", action="store_false", help="remove output colors", dest="color", default=None)
    parser.add_argument(
        "-y", "--assumeyes", action="store_true", help="Automatically answer yes for all questions", default=False
    )
    subparsers = parser.add_subparsers(description="Available commands", dest="MAIN_command", required=True)

    coresponds = init_commands(list_commands(), subparsers)
    options = parse_options(coresponds, parser, arguments)

    command, _ = coresponds[options["MAIN_command"]]

    color = DotConfigRc().configprofile.get("color", True)
    if isinstance(options["color"], bool):
        color = options.pop("color")
    # set color
    Style().config(color=color)

    try:
        return command.handle(**options)
    except KeyboardInterrupt:
        return 100


def cli():
    exit(main(sys.argv[1:]))


if __name__ == "__main__":
    cli()
