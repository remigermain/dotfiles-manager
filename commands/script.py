import argparse
from fnmatch import fnmatch
from pathlib import Path

from .base import CommandAbstract, SubCommandAbstract


def globscript(path, scripts_name=None, match=False):
    scripts = list(path.glob("*.sh"))

    if not scripts_name:
        return scripts

    results = []
    for script in scripts:
        name = script.with_suffix("").name
        if match:
            for sub in scripts_name:
                if fnmatch(name, f"*{sub}*"):
                    results.append(script)
        elif name in scripts_name:
            results.append(script)

    return list(set(results))


class CommandScript(SubCommandAbstract):
    help = "run script by command"

    class Run(CommandAbstract):
        help = "run script by command"

        def add_arguments(self, parser: argparse.ArgumentParser):
            choices = self.config.get("commands", [])
            parser.add_argument("script-command", help="name to run script command", choices=choices)

            parser.add_argument("scripts-name", nargs="*", help="run only name script specified (default to all)")
            parser.add_argument("--match", action="store_true", default=False, help="any match name")

        def handle(self, match, **options):
            script_command = options["script-command"]
            scripts_name = options["scripts-name"]

            scripts = globscript(self.config.fs.lpath(script_command), scripts_name, match)
            if not scripts:
                self.stdout.info("no script to run...")
                return

            for script in scripts:
                self.stdout.write(f"run {script_command} {self.style.info(script.name)}")

    class List(CommandAbstract):
        help = "list all installed scripts"

        def handle(self, **options):
            commands = self.config.get("commands", [])

            for choice in commands:
                for script in globscript(self.config.fs.lpath(choice)):
                    self.stdout.info(f"[{choice}] {script}")

    class Add(CommandAbstract):
        help = "add script for command"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("script-command", help="command name")
            parser.add_argument("scripts", nargs="+", help="scripts to add")

        def handle(self, scripts, **options):
            script_command = options["script-command"]

            dest = self.config.fs.lpath(script_command)
            for script in scripts:
                source = Path(script).expanduser().resolve()
                self.config.fs.copy(source, dest / source.name)
                self.stdout.info(f"add command Script {script_command} -> {source}")
