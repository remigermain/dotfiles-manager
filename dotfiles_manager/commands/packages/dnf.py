import json

from dotfiles_manager.commands.base import SubCommandAbstract, command
from dotfiles_manager.utils.shell import run


class CommandDnf(SubCommandAbstract):
    help = "dnf integration"

    @command(help="backup all installed packages")
    def backup(self, **option):
        self.stdout.write("backup ", self.style.info("dnf"), " apps...")
        res = run(["dnf", "repoquery", "--userinstalled", "--qf", "%{name}"])
        if not res:
            return self.stderr.error("invalid response from dnf")

        packages = sorted({e.strip().split(":")[0].strip() for e in res.stdout.strip().split("\n")})

        with self.config.fs.lbase("dnf.json").open("w") as f:
            json.dump(packages, f, indent=4)

    @command(help="update all installed packages")
    def update(self, **option):
        self.stdout.write("update ", self.style.info("dnf"), " apps...")

        path = self.config.fs.lbase("dnf.json")
        if not path.exists():
            return
        path = self.config.fs.lbase("dnf.conf")
        with path.open() as f:
            pkgs = json.load(f)

        res = run(["dnf", "--best", "install", *pkgs], capture_output=False)
        if not res:
            return self.stderr.error("invalid response from dnf")
