import json
from tempfile import NamedTemporaryFile

from dotfiles_manager.commands.base import SubCommandAbstract, command
from dotfiles_manager.utils.shell import run


class CommandGnome(SubCommandAbstract):
    help = "gnome integration"

    @command(help="backup all installed packages")
    def backup(self, **options):
        self.stdout.write("backup ", self.style.info("gnome extension"), " apps...")
        res = run(["gext", "list", "--only-uuid"])
        if not res:
            return self.stderr.error("invalid response from gnome_extension_cli")

        path = self.config.fs.lbase("gnome.json")
        packages = sorted({e.strip() for e in res.stdout.strip().split("\n")})

        with path.open("w") as f:
            json.dump(packages, f, indent=4)

    @command(help="update all installed packages")
    def update(self, **option):
        self.stdout.write("update ", self.style.info("gnome extension"), " apps...")

        path = self.config.fs.lbase("gnome.txt")
        if not self.config.fs.exist(path):
            return

        with path.open("r") as f:
            pkgs = f.readlines()
            res = run(["gext", "install", *pkgs], capture_output=False)
            if not res:
                return self.stderr.error("invalid response from gnome_extension_cli")
