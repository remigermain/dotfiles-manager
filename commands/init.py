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
            if not self.stdout.write.accept("profiles", self.style.info(repr(profile)), " already exists, continue?"):
                return

        self.rc["profiles"][profile] = {"directory": str(directory)}
        self.stdout.write(f"profil {profile!r} linked to {directory}")
