from .base import CommandAbstract


class Update(CommandAbstract):
    name = "update"
    description = "update all files"

    def run(self, config, base, flags):
        self.exec_command(["link", "update"])
        self.exec_command(["copy", "update"])
        self.exec_command(["pkg"])
        self.exec_command(["config", "update", "--tags=update"])
