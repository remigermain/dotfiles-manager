import subprocess

from commands.base import CommandAbstract, SubCommandAbstract
from utils.conf import ConfigScope


def bincode():
    if subprocess.run(["which", "code"], capture_output=True).returncode == 0:
        return "code"
    if subprocess.run(["which", "codium"], capture_output=True).returncode == 0:
        return "codium"
    return


class CommandVSCode(SubCommandAbstract):
    help = "vscode/codium integration"

    class Backup(CommandAbstract):
        help = "backup all installed packages"

        def handle(self, **option):
            config = ConfigScope.from_name(CommandVSCode.name)
            code = bincode()
            if not code:
                return

            res = subprocess.run([code, "--list-extensions"], capture_output=True)
            if not res:
                self.stderr.error(f"Invalid response from {code}")

            packages = [e.strip() for e in res.stdout.decode().strip().split("\n")]

            config.set("packages", list(set(packages)))

    class Update(CommandAbstract):
        help = "update all installed packages"

        def add_arguments(self, parser):
            parser.add_argument("-f", "--force", action="store_true", default=True, help="force")

        def handle(self, force, **option):
            config = ConfigScope.from_name(CommandVSCode.name)
            code = bincode()
            if not code:
                return

            pkgs = config.get("packages", [])
            if not pkgs:
                return

            cmds = [code]
            if force:
                pkgs.append("--force")

            for pkg in pkgs:
                cmds.extend(("--install-extension", pkg))

            subprocess.run(cmds)
