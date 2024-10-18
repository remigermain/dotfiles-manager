import argparse

from utils.config import DotfileRC

from .base import CommandAbstract


class CommandUse(CommandAbstract):
    name = "use"
    help = "use different profile"

    def add_arguments(self, parser: argparse.ArgumentParser):
        config = DotfileRC()
        choices = config["profiles"].keys()
        parser.add_argument("profile", help="name of the profil", choices=choices)

    def handle(self, profile, **options):
        config = DotfileRC()
        config["profile"] = profile
        self.stdout.success(f"switched to {profile}...")
        config.save()
