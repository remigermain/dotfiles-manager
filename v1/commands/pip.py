from .base import CommandAbstract


class Pip(CommandAbstract):
    description = "python packages"
    directory = "packages/python"

    def add_arguments(self, parser):
        sub = parser.add_subparsers(description="Available commands", dest="action", required=True)

        sub.add_parser("install", help="install packages")
        sub.add_parser("backup", help="backup packages")
        sub.add_parser("update", help="update packages")

    def run(self, config, base, flags):
        base = base / "requirements.txt"

        if flags.action == "install":
            self.install(config, base, flags)
        elif flags.action == "update":
            self.update(config, base, flags)
        elif flags.action == "backup":
            self.backup(config, base, flags)

    def install(self, config, base, flags):
        self.logger.show("install python pip...")
        self.sh.exec(["python3", "-m", "pip", "install", "--upgrade", "pip"])

        if base.exists():
            self.logger.show("install python packages...")
            self.sh.exec(["python3", "-m", "pip", "install", "--ingore-installed", "-r", base])

    def update(self, config, base, flags):
        self.logger.show("update python pip...")
        self.sh.exec(["python3", "-m", "pip", "install", "--upgrade", "pip"])

        if base.exists():
            self.logger.show("update python packages...")
            self.sh.exec(["python3", "-m", "pip", "install", "--upgrade", "-r", base])

    def backup(self, config, base, flags):
        self.logger.show("backup flatpak packages...")

        results = self.sh.exec(["python3", "-m", "pip", "freeze"])

        requirements = results.stdout.decode()
        with open(base, "w") as f:
            f.write(requirements)
