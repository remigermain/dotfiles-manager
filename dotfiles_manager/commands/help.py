import argparse

from dotfiles_manager.commands.base import CommandAbstract
from dotfiles_manager.utils.commands import require_config, require_rc


@require_rc(False)
@require_config(False)
class CommandHelp(CommandAbstract):
    help = "show help"
    aliases = ("h",)

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("command-help", nargs="*", help="Show command help")

    def handle(self, parser, list_commands, **options):
        commands = options.get("command-help") or []
        lst_commands = list_commands.copy()

        for idx, command in enumerate(commands, start=1):
            if command not in lst_commands:
                return self.stderr.write("not found command ", self.style.error(command))

            cmd, parser = lst_commands[command]
            if idx == len(commands):
                break

            try:
                lst_commands = cmd.subcommands()
            except NotImplementedError:
                return self.stderr.write("not found command ", self.style.error(command))

        parser.print_help(self.stdout._stream)
