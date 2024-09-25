from .base import CommandAbstract


class Backup(CommandAbstract):
    description = "backup all files"

    def run(self, config, base, flags):
        self.exec_command(["flatpak", "backup"])
        self.exec_command(["config", "backup"])
