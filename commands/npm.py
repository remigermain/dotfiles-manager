from .base import CommandAbstract


class Npm(CommandAbstract):
    description = "npm packages"
    directory = None

    def add_arguments(self, parser):
        sub = parser.add_subparsers(description="Available commands", dest="action", required=True)

        sub.add_parser("install", help="install packages")
        sub.add_parser("update", help="update packages")

    def run(self, config, base, flags):
        if flags.action == "install":
            self.install(config, base, flags)
        elif flags.action == "update":
            self.update(config, base, flags)

    def install(self, config, base, flags):
        self.logger.show("install npm...")
        self.sh.exec(["npm", "install", "-g"])

    def update(self, config, base, flags):
        self.logger.show("upgrade npm...")
        self.sh.exec(["npm", "upgrade", "-g", "--save"])
