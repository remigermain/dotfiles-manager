import argparse
from pathlib import Path

from dotfiles_manager.commands.base import CommandAbstract
from dotfiles_manager.utils.commands import require_config, require_rc
from dotfiles_manager.utils.config import DEFAULT_PROFILE, Config


@require_rc(False)
@require_config(False)
class CommandCreate(CommandAbstract):
    help = "create dotfile"

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("configpath", type=Path, nargs="?", default="./", help="where to initiliase repo")

    def handle(self, configpath: Path, **options):
        configpath = configpath.expanduser()
        if configpath.is_dir():
            configpath /= "dotfile.json"
        config = Config(configpath)
        config.save()
        self.stdout.write("config created ", self.style.info(configpath), "")
