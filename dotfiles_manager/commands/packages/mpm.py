import argparse
from tempfile import NamedTemporaryFile

from dotfiles_manager.commands.base import CommandAbstract, SubCommandAbstract, command
from dotfiles_manager.utils.shell import run


class CommandMpm(SubCommandAbstract):
    help = "mpm integration"

    class Add(CommandAbstract):
        help = "add manager"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("managers", nargs="+", help="managers")

        def handle(self, managers: list[str], **options):
            managers_lst = self.config.get("managers", [])
            managers = sorted(set(managers_lst) | set(managers))
            self.config.set("managers", managers)
            self.stdout.write("managers updated to")
            for manager in managers:
                self.stdout.write(" - ", self.style.info(manager))

    @command(help="backup all installed packages")
    def backup(self: SubCommandAbstract, assumeyes, **option):
        managers = self.config.get("managers", [])

        if not managers:
            return self.stdout.warning("no mangers sets...")

        cmds = ["mpm"]
        cmds.extend(f"--{m}" for m in managers)
        cmds.append("backup")

        with NamedTemporaryFile("w", suffix=".toml") as f:
            cmds.extend(["--force", f.name])

            if not run(cmds, capture_output=False):
                return self.stderr.error("invalid response from mpm...")

            with open(f.name) as toml, self.config.fs.lbase("mpm.toml").open("w") as f:
                # remove first 3 line of mpm ( timespace, info ...)
                f.write("".join(toml.readlines()[3:]))

    @command(help="update all installed packages")
    def update(self, **option):
        print("update")
