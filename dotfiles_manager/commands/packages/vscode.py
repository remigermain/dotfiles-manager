from typing import Optional

from dotfiles_manager.commands.base import CommandAbstract, SubCommandAbstract
from dotfiles_manager.utils.shell import run


def bincode() -> Optional[str]:
    if run(["which", "code"], showerror=False).returncode == 0:
        return "code"
    if run(["which", "codium"], showerror=False).returncode == 0:
        return "codium"
    return


class CommandVSCode(SubCommandAbstract):
    help = "vscode/codium integration"

    class Backup(CommandAbstract):
        help = "backup all installed packages"

        def handle(self, **option):
            code = bincode()
            if not code:
                return

            self.stdout.write("backup ", self.style.info(code), " apps...")
            res = run([code, "--list-extensions"], sudo=False)
            if not res:
                return self.stderr.error(f"Invalid response from {code}")

            packages = [e.strip() for e in res.stdout.strip().split("\n")]

            self.config.set("packages", list(set(packages)))

    class Update(CommandAbstract):
        help = "update all installed packages"

        def add_arguments(self, parser):
            parser.add_argument("-f", "--force", action="store_true", default=True, help="force")

        def handle(self, force, **option):
            code = bincode()
            if not code:
                return

            pkgs = self.config.get("packages", [])
            if not pkgs:
                return

            cmds = [code]
            if force:
                pkgs.append("--force")

            for pkg in pkgs:
                cmds.extend(("--install-extension", pkg))

            self.stdout.write("update ", self.style.info(code), " apps...")
            return run(cmds, sudo=False, capture_output=False)
