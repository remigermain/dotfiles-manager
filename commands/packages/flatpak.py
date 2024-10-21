import argparse
import subprocess

from commands.base import CommandAbstract, SubCommandAbstract


class CommandFlatpak(SubCommandAbstract):
    help = "flatpak integration"

    class Backup(CommandAbstract):
        help = "backup all installed packages"

        def handle(self, **option):
            self.stdout.write("backup ", self.style.info("flatpak"), " apps...")
            res = subprocess.run(["flatpak", "list", "--app", "--columns=application"], capture_output=True)
            if not res:
                return self.stderr.error("invalid response from flatpak")

            packages = [e.strip() for e in res.stdout.decode().strip().split("\n")]

            self.config.set("packages", packages)

    class Update(CommandAbstract):
        help = "update all installed packages"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("-y", "--assumeyes", help="Automatically answer yes for all questions")

        def handle(self, **option):
            self.stdout.write("update ", self.style.info("flatpak"), " apps...")
            pkgs = self.config.get("packages", [])
            res = subprocess.run(["flatpak", "install", "--or-update", *pkgs])
            if not res:
                return self.stderr.error("invalid response from flatpak")
