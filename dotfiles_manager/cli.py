#!/usr/bin/env python3
import argparse
import sys

from dotfiles_manager.commands.copy import copy_command
from dotfiles_manager.commands.extra import backup_command, refresh_command
from dotfiles_manager.commands.init import (
    init_command,
    init_copy_command,
    init_link_command,
)
from dotfiles_manager.commands.runner import runner
from dotfiles_manager.commands.symlink import link_command, unlink_command
from dotfiles_manager.utils.style import style

type = argparse.FileType()


def main():
    parser = argparse.ArgumentParser("dotfiles manager")
    parser.add_argument(
        "-y", action="store_true", default=False, help="assume yes"
    )
    parser.add_argument(
        "-n", action="store_true", default=False, help="assume no"
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
        "--only",
        choices=["home", "system"],
        help="link only specified element",
        default=None,
        dest="only",
    )
    init.add_argument("--config", help="config path", default=[], nargs="+")

    init_link = sub.add_parser("init-link", help="symlink all dotfiles")
    init_link.add_argument(
        "--only",
        choices=["home", "system"],
        help="link only specified element",
        default=None,
        dest="only",
    )

    init_copy = sub.add_parser("init-copy", help="copy all dotfiles")
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

    sub.add_parser(
        "backup",
        aliases=("bc",),
        help="backup dotfiles, show diff, and push to git",
    )
    sub.add_parser(
        "refresh",
        aliases=("up", "update", "upgrade"),
        help="run a refreshs scripts (update packages ..ect)",
    )

    flags = parser.parse_args()

    style.config(flags)

    try:
        match flags.command:
            case "init":
                runner(init_command(flags), flags)
            case "init-link":
                runner(init_link_command(flags), flags)
            case "init-copy":
                runner(init_copy_command(flags), flags)
            case "link" | "ln":
                runner(link_command(flags.src, flags), flags)
            case "unlink" | "ul":
                runner(unlink_command(flags.src, flags), flags)
            case "copy" | "cp":
                runner(copy_command(flags.src, flags), flags)
            case "backup" | "bc":
                backup_command(flags)
            case "refresh" | "up" | "upgrade" | "update":
                refresh_command(flags)
            case _:
                sys.exit(f"invalid command {flags.command!r}")
    except KeyboardInterrupt:
        exit(1)
