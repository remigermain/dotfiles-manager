import argparse
import subprocess
from fnmatch import fnmatch
from pathlib import Path
from typing import Optional

from .base import CommandAbstract, SubCommandAbstract


class CommandScript(SubCommandAbstract):
    help = "run script by command"

    class Run(CommandAbstract):
        help = "run script by command"

        def add_arguments(self, parser: argparse.ArgumentParser):
            choices = self.config.get("commands", {}).keys()
            parser.add_argument(
                "script-command", dest="script_command", help="name to run script command", choices=choices
            )

            parser.add_argument(
                "scripts-name",
                dest="scripts_name",
                nargs="*",
                help="run only name script specified (default to all)",
                default=[],
            )
            parser.add_argument("--match", action="store_true", default=False, help="any match name")
            parser.add_argument("--ignore", nargs="*", dest="ignores", help="ignore scripts", default=[])

        def handle(
            self, script_command: str, ignores: list[str], match: bool, scripts_name: Optional[str] = None, **options
        ):
            commands = self.config.get("commands", {})
            scripts = commands.get(script_command, [])
            scripts = self.matchs(scripts, scripts_name, ignores, match)

            if not scripts:
                self.stdout.info("no script to run...")
                return

            self.stdout.write(f"[{self.style.info(script_command)}]")
            for script in scripts:
                script = self.config.fs.lpath(Path(script_command) / script)
                self.stdout.write("run ", self.style.info(script.name))
                try:
                    subprocess.run([str(script)], check=True)
                except Exception as e:
                    self.stdout.error(f" {e}")

        def matchs(self, scripts: list[str], pattern: Optional[list[str]], ignores: list[str], match: bool) -> set[str]:
            filterd = set()

            if not pattern:
                pattern = scripts

            for script in scripts:
                for pat in pattern:
                    pat = f"*{pat}*" if match else pat
                    if fnmatch(script, pat):
                        filterd.add(script)

            for script in list(filterd):
                for pat in ignores:
                    pat = f"*{pat}*" if match else pat
                    if fnmatch(script, pat):
                        filterd.discard(script)

            return filterd

    class List(CommandAbstract):
        help = "list all installed scripts"

        def handle(self, **options):
            for command, scripts in self.config.get("commands", {}).items():
                self.stdout.write(f"[{self.style.info(command)}]")
                for script in scripts:
                    self.stdout.write(" - ", self.style.info(script))

    class Add(CommandAbstract):
        help = "add script for command"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("script-command", dest="script_command", help="command name")
            parser.add_argument("scripts", nargs="+", help="scripts to add")

        def handle(self, script_command: str, scripts: list[str], **options):
            commands = self.config.get("commands", {})
            list_scripts = commands.setdefault(script_command, [])

            self.stdout.write("[", self.style.info(script_command), "]")
            for script in scripts:
                script = Path(script).expanduser().resolve()

                if script.name in list_scripts:
                    if not self.stdout.warning.accept("a script with the same name exists, replace it ?"):
                        continue

                dest = self.config.fs.lpath(Path(script_command) / script.name)
                self.config.fs.copy(script, dest)
                self.config.fs.chmod(dest, 0o774)
                self.stdout.write("add ", self.style.info(script.name))
                list_scripts.append(script.name)

            commands[script_command] = set(list_scripts)
            self.config.set("commands", commands)
