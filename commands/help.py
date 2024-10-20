import argparse

from .base import CommandAbstract


class CommandHelp(CommandAbstract):
    help = "show help"
    aliases = ("h",)

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("command-help", nargs="?", help="Show command help")

    def handle(self, parser, list_commands, **options):
        command = options.get("command-help")
        if command:
            if command not in list_commands:
                return self.stderr.write("invalid command ", self.style.error(command))
            _, parser = list_commands[command]
        parser.print_help(self.stdout._stream)
