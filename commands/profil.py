import argparse
import json

from utils.utils import cast

from .base import CommandAbstract, SubCommandAbstract


class CommandProfil(SubCommandAbstract):
    name = "profil"
    help = "profil settings"

    class Use(CommandAbstract):
        help = "use different profil"

        def add_arguments(self, parser: argparse.ArgumentParser):
            choices = self.rc["profiles"].keys()
            parser.add_argument("profile", help="name of the profil", choices=choices)

        def handle(self, profile, **options):
            self.rc["profile"] = profile
            self.stdout.success(f"switched to {profile}...")
            self.rc.save()

    class Set(CommandAbstract):
        help = "set settings to profil"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("settings", nargs="+", help="settings")

        def handle(self, settings: list[str], **options):
            profilesettings = self.rc.configprofile
            for element in settings:
                key, value = element.split("=", 1)
                profilesettings[key] = cast(value)
                self.stdout.success(f"set {key}={value}")

            self.rc.save()

    class Config(CommandAbstract):
        help = "show settings profils"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("--raw", action="store_true", help="prinf config not formated (in json)")

        def handle(self, raw, **options):
            profiles = self.rc["profiles"]
            usedprofil = self.rc["profile"]

            if raw:
                self.stdout.write(json.dumps(self.rc, indent=4))
                return

            for idx, (profil, settings) in enumerate(profiles.items()):
                used = ""
                if profil == usedprofil:
                    used = f" <- {self.style.warning("used")}"
                self.stdout.write(f"[{self.style.info(profil)}]{used}")
                for key, value in settings.items():
                    self.stdout.write(f"{key}={value}")
                if idx == len(profiles):
                    self.stdout.write("\n")
