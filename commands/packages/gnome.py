import subprocess

from commands.base import CommandAbstract, SubCommandAbstract


class CommandGnome(SubCommandAbstract):
    help = "gnome integration"

    class Backup(CommandAbstract):
        help = "backup all installed packages"

        def handle(self, **option):
            self.stdout.write("backup ", self.style.info("gnome extension"), " apps...")
            res = subprocess.run(["gext", "list", "--only-uuid"], capture_output=True)
            if not res:
                return self.stderr.error("invalid response from gnome_extension_cli")

            packages = [e.strip() for e in res.stdout.decode().strip().split("\n")]

            self.config.set("packages", packages)

    class Update(CommandAbstract):
        help = "update all installed packages"

        def handle(self, **option):
            self.stdout.write("update ", self.style.info("gnome extension"), " apps...")
            pkgs = self.config.get("packages", [])
            if not pkgs:
                return

            res = subprocess.run(["gext", "install", *pkgs])
            if not res:
                return self.stderr.error("invalid response from gnome_extension_cli")
