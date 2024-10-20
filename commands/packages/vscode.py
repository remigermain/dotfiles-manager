import subprocess

from commands.base import CommandAbstract, SubCommandAbstract


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
            code = bincode()
            if not code:
                return

            self.stdout.write("backup ", self.style.info(code), " apps...")
            res = subprocess.run([code, "--list-extensions"], capture_output=True)
            if not res:
                self.stderr.error(f"Invalid response from {code}")

            packages = [e.strip() for e in res.stdout.decode().strip().split("\n")]

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
            subprocess.run(cmds)
