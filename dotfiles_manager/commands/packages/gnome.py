from dotfiles_manager.commands.base import CommandAbstract, SubCommandAbstract
from dotfiles_manager.utils.shell import run


class CommandGnome(SubCommandAbstract):
    help = "gnome integration"

    class Backup(CommandAbstract):
        help = "backup all installed packages"

        def handle(self, **option):
            self.stdout.write("backup ", self.style.info("gnome extension"), " apps...")
            res = run(["gext", "list", "--only-uuid"])
            if not res:
                return self.stderr.error("invalid response from gnome_extension_cli")

            packages = {e.strip() for e in res.stdout.strip().split("\n")}

            self.config.set("packages", sorted(packages))

    class Update(CommandAbstract):
        help = "update all installed packages"

        def handle(self, **option):
            self.stdout.write("update ", self.style.info("gnome extension"), " apps...")
            pkgs = self.config.get("packages", [])
            if not pkgs:
                return

            res = run(["gext", "install", *pkgs], capture_output=False)
            if not res:
                return self.stderr.error("invalid response from gnome_extension_cli")
