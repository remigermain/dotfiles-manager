import argparse
from pathlib import Path

from utils.commands import require_config, require_rc
from utils.config import DEFAULT_PROFILE

from .base import CommandAbstract


@require_rc(False)
@require_config(False)
class CommandInit(CommandAbstract):
    name = "init"
    help = "initialise dotfile"

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("configpath", type=Path, help="where to initiliase repo")
        parser.add_argument("profile", nargs="?", default=DEFAULT_PROFILE, help="profile")

    def handle(self, configpath: Path, profile, **options):
        configpath = configpath.expanduser().resolve()
        if profile in self.rc["profiles"]:
            if not self.stdout.write.accept("profiles ", self.style.info(profile), " already exists, continue?"):
                return

        self.rc["profiles"][profile] = {"directory": str(configpath)}
        self.stdout.write(f"profil {self.style.info(profile)} added to {configpath}")
        self.rc.save()
