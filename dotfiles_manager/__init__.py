#!/usr/bin/env python3
import argparse
import sys

from dotfiles_manager.commands.copy import copy_command
from dotfiles_manager.commands.script import script_command
from dotfiles_manager.commands.init import (
    init_command,
    init_copy_command,
    init_link_command,
)
from dotfiles_manager.commands.runner import runner
from dotfiles_manager.commands.symlink import link_command, unlink_command
from dotfiles_manager.utils.style import style
from dotfiles_manager.utils.logger import logger
from dotfiles_manager.utils.config import MAP_SCRIPTS_UNIQUE, MAP_SCRIPTS

type = argparse.FileType()


def main():
    parser = argparse.ArgumentParser("dotfiles manager")
    parser.add_argument(
        "-y", "--yes", action="store_true", default=False, help="assume yes"
    )
    parser.add_argument(
        "-n", "--no", action="store_true", default=False, help="assume no"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        const=10,
        dest="verbose",
        action="append_const",
        help="verbose",
    )
    parser.add_argument(
        "--sudo",
        dest="sudo",
        action="store_true",
        help="run all command in sudo",
        default=False,
    )
    parser.add_argument(
        "-c",
        "--no-color",
        action="store_true",
        default=False,
        help="not color output",
    )
    sub = parser.add_subparsers(title="commands", dest="command", required=True)

    init = sub.add_parser("init", help="symlink/copy all dotfiles")
    init.add_argument(
        "--interactive",
        action="store_true",
        help="ask confirmation for each action",
        default=False,
    )
    init.add_argument(
        "--only",
        choices=["home", "system"],
        help="link only specified element",
        default=None,
        dest="only",
    )
    init.add_argument("--config", help="config path", default=[], nargs="+")

    init_link = sub.add_parser("init-link", help="symlink all dotfiles")
    init_link.add_argument(
        "--interactive",
        action="store_true",
        help="ask confirmation for each action",
        default=False,
    )
    init_link.add_argument(
        "--only",
        choices=["home", "system"],
        help="link only specified element",
        default=None,
        dest="only",
    )

    init_copy = sub.add_parser("init-copy", help="copy all dotfiles")
    init_copy.add_argument(
        "--interactive",
        action="store_true",
        help="ask confirmation for each action",
        default=False,
    )
    init_copy.add_argument(
        "--only",
        choices=["home", "system"],
        help="link only specified element",
        default=None,
        dest="only",
    )
    init_copy.add_argument(
        "--config", help="config path", default=[], nargs="+"
    )

    link = sub.add_parser("link", aliases=("ln",), help="link dotfiles file(s)")
    link.add_argument("src", help="file/dir to add link", nargs="+")

    link = sub.add_parser(
        "unlink", aliases=("ul",), help="unlink dotfiles file(s)"
    )
    link.add_argument("src", help="file/dir to remove link", nargs="+")
    link.add_argument(
        "--no-remove",
        action="store_true",
        default=False,
        help="no remove dotfiles linked",
    )

    copy = sub.add_parser("copy", aliases=("cp",), help="copy dotfiles file(s)")
    copy.add_argument("src", help="file/dir to copy", nargs="+")

    run = sub.add_parser("run", help="run script name")
    run.add_argument("script", help="scripts name", choices=MAP_SCRIPTS_UNIQUE)
    run.add_argument("*", help="args to pass to scripts", nargs="*")

    # add all script without extentios
    for name in MAP_SCRIPTS_UNIQUE:
        script_parser = sub.add_parser(name, help=f"script command {name!r}")
        script_parser.add_argument(
            "*", help="args to pass to scripts", nargs="*"
        )

    flags = parser.parse_args()
    if "interactive" in flags and flags.interactive is True:
        flags.no = False
        flags.yes = True

    style.config(flags)
    if flags.verbose:
        logger.setLevel(50 - sum(flags.verbose))
    else:
        logger.setLevel(10000000)

    logger.debug("flags: %s", flags)

    try:
        logger.info("Run command: %s", flags.command)
        if flags.command == "init":
            runner(init_command(flags), flags)
        elif flags.command == "init-link":
            runner(init_link_command(flags), flags)
        elif flags.command == "init-copy":
            runner(init_copy_command(flags), flags)
        elif flags.command in ("link", "ln"):
            runner(link_command(flags.src, flags), flags)
        elif flags.command in ("unlink", "ul"):
            runner(unlink_command(flags.src, flags), flags)
        elif flags.command in ("copy", "cp"):
            runner(copy_command(flags.src, flags), flags)
        elif flags.command == "run":
            script_command(MAP_SCRIPTS[flags.script], flags)
        elif flags.command in MAP_SCRIPTS:
            script_command(MAP_SCRIPTS[flags.command], flags)
        else:
            sys.exit(f"invalid command {flags.command!r}")
    except KeyboardInterrupt:
        exit(1)


def cli():
    exit(main())


if __name__ == "__main__":
    cli()
