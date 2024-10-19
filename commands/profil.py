import argparse

from utils.config import DotfileRC
from utils.utils import cast

from .base import CommandAbstract, SubCommandAbstract


class CommandProfil(SubCommandAbstract):
    name = "profil"
    help = "profil settings"

    class Use(CommandAbstract):
        help = "use different profil"

        def add_arguments(self, parser: argparse.ArgumentParser):
            config = DotfileRC()
            choices = config["profiles"].keys()
            parser.add_argument("profile", help="name of the profil", choices=choices)

        def handle(self, profile, **options):
            config = DotfileRC()
            config["profile"] = profile
            self.stdout.success(f"switched to {profile}...")

    class Set(CommandAbstract):
        help = "set settings to profil"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("settings", nargs="+", help="settings")

        def handle(self, settings: list[str], **options):
            config = DotfileRC()
            configprofil = config["profiles"][config["profile"]]
            for element in settings:
                key, value = element.split("=", 1)
                configprofil[key] = cast(value)
                self.stdout.success(f"set {key}={value}")

    class show(CommandAbstract):
        help = "show settings profil"

        def handle(self, **options):
            config = DotfileRC()
            configprofil = config["profiles"][config["profile"]]
            for key, value in configprofil.items():
                self.stdout.write(f"{key}={value}")
