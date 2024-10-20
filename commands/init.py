import argparse
import os
import subprocess
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
            res = self.stdout.info.input(f"profiles {profile!r} already exists, continue?[y-n]").lower()
            if res != "y":
                return

        self.rc["profiles"][profile] = {"directory": str(directory)}
        self.stdout.write(f"profil {profile!r} linked to {directory}")

        # TODO create group
        subprocess.run(["sudo", "chmod", "770", self.rc.path])
        subprocess.run(["sudo", "chown", os.getenv("USER"), self.rc.path])
