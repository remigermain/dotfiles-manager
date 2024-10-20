import argparse
from pathlib import Path

from .base import CommandAbstract


class CommandInit(CommandAbstract):
    name = "init"
    help = "initialise dotfile"

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("directory", type=Path, nargs="?", default=".", help="where to initilisae repo")
        parser.add_argument("-p", "--profile", default="base", help="profile")

    def handle(self, directory: Path, profile, **options):
        directory = directory.expanduser().resolve()
        if profile in self.rc["profiles"]:
            res = self.stdout.input(f"profiles {profile!r} already exists, continue?[y-n]").lower()
            if res != "y":
                return

        self.rc["profiles"][profile] = {"directory": str(directory)}
        self.stdout.write(f"profil {profile!r} linked to {directory}")
