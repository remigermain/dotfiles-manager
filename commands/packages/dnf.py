import argparse

from commands.base import CommandAbstract, SubCommandAbstract
from utils.shell import run


class CommandDnf(SubCommandAbstract):
    help = "dnf integration"

    class Backup(CommandAbstract):
        help = "backup all installed packages"

        def handle(self, **option):
            self.stdout.write("backup ", self.style.info("dnf"), " apps...")
            res = run(["dnf", "repoquery", "--userinstalled", "--qf", "%{name}"])

            if not res:
                return self.stderr.error("invalid response from dnf")

            packages = [e.strip().split(":")[0].strip() for e in res.decode().strip().split("\n")]

            self.config.set("packages", packages)

    class Update(CommandAbstract):
        help = "update all installed packages"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("-y", "--assumeyes", help="Automatically answer yes for all questions")

        def handle(self, **option):
            self.stdout.write("update ", self.style.info("dnf"), " apps...")
            pkgs = self.config.get("packages", [])
            res = run(["dnf", "--best", "install", *pkgs], capture_output=False)
            if not res:
                return self.stderr.error("invalid response from dnf")
