import argparse
import json

from dotfiles_manager.commands.base import SubCommandAbstract, command
from dotfiles_manager.utils.shell import run


class CommandFlatpak(SubCommandAbstract):
    help = "flatpak integration"

    @command(help="backup all installed packages")
    def backup(self, **option):
        self.stdout.write("backup ", self.style.info("flatpak"), " apps...")
        res = run(["flatpak", "list", "--app", "--columns=application"], sudo=False)
        if not res:
            return self.stderr.error("invalid response from flatpak")

        packages = sorted({e.strip() for e in res.stdout.strip().split("\n")})

        with self.config.fs.lbase("flatpak.json").open("w") as f:
            json.dump(packages, f)

    @command(help="update all installed packages")
    def update(self, **option):
        self.stdout.write("update ", self.style.info("flatpak"), " apps...")

        with self.config.fs.lbase("flatpak.json").open("w") as f:
            pkgs = json.load(f)
            res = run(["flatpak", "install", "--or-update", *pkgs], sudo=False, capture_output=False)
            if not res:
                return self.stderr.error("invalid response from flatpak")
