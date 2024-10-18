import enum
from pathlib import Path

from .base import CommandAbstract


class ConfigEnum(enum.StrEnum):
    COMMAND = enum.auto()
    SCRIPT = enum.auto()


class Config(CommandAbstract):
    description = "config system"

    def add_arguments(self, parser):
        sub = parser.add_subparsers(description="Available commands", dest="action", required=True)

        parser_add = sub.add_parser("add", help="add config elements")

        default_tags = "update"

        parser_update = sub.add_parser("update", help="run all command scripts")
        parser_update.add_argument("--tags", default=default_tags, help="run only with tags matchs")

        action_add = parser_add.add_subparsers(description="Available commands", dest="action_add", required=True)

        parser_script = action_add.add_parser("script", help="add script")
        parser_script.add_argument("file", help="file script to run")
        parser_script.add_argument("--tags", default=default_tags, help="add tags to elements")

        parser_command = action_add.add_parser("command", help="add command")
        parser_command.add_argument("commands", nargs="+", help="command")
        parser_command.add_argument("--tags", default=default_tags, help="add tags to elements")

    def run(self, config, base, flags):
        if flags.action == "add":
            self.add(config, base, flags)
        elif flags.action == "update":
            self.update(config, base, flags)

    def add(self, config, base, flags):
        element = {"tags": flags.tags}
        if flags.action_add == "command":
            element["data"] = flags.commands
            element["type"] = ConfigEnum.COMMAND
        else:
            flags.file = self.sanitize_path(flags.file)
            output = self.sanitize_path(base / flags.file.name)
            if self.final_path(flags.file) != self.final_path(output):
                self.logger.show(f"copy script file {str(flags.file)!r}...")
                self.sh.cp(flags.file, output)

            element["data"] = Path("config") / flags.file.name
            element["type"] = ConfigEnum.SCRIPT

        config.config.append(element)

    def update(self, config, base, flags):
        tags = flags.tags.split(":")
        for el in config.config:
            el_tags = el.tags.split(":")
            if not (set(tags) & set(el_tags)):
                continue

            if el["type"] == ConfigEnum.SCRIPT:
                cmd = Path(el["data"])
            else:
                cmd = el["data"]
            self.sh.exec(cmd)
