import subprocess

from commands.base import CommandAbstract, SubCommandAbstract
from utils.conf import ConfigScope


class CommandGnome(SubCommandAbstract):
    help = "gnome integration"

    class Backup(CommandAbstract):
        help = "backup all installed packages"

        def handle(self, **option):
            config = ConfigScope.from_name(CommandGnome.name)
            res = subprocess.run(["gext", "list", "--only-uuid"], capture_output=True)
            if not res:
                self.stderr.error("Invalid response from gnome_extention_cli")

            packages = [e.strip() for e in res.stdout.decode().strip().split("\n")]

            config.set("packages", packages)

    class Update(CommandAbstract):
        help = "update all installed packages"

        def handle(self, **option):
            config = ConfigScope.from_name(CommandGnome.name)
            pkgs = config.get("packages", [])
            if pkgs:
                res = subprocess.run(["gext", "install", *pkgs])
                if not res:
                    self.stderr.error("Invalid response from gnome_extention_cli")
