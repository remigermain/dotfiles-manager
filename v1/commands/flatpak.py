from .base import CommandAbstract


class Flatpak(CommandAbstract):
    description = "flatpak info"
    directory = "packages/flatpak"

    def add_arguments(self, parser):
        sub = parser.add_subparsers(description="Available commands", dest="action", required=True)

        sub.add_parser("install", help="install packages")
        sub.add_parser("backup", help="backup packages")
        sub.add_parser("update", help="update packages")

    def packages(self, file):
        if file.exists():
            return [f.strip() for f in file.open().readlines() if f.strip()]
        return []

    def run(self, config, base, flags):
        base = base / "flatpak.txt"

        if flags.action == "install":
            self.install(config, base, flags)
        elif flags.action == "update":
            self.update(config, base, flags)
        elif flags.action == "backup":
            self.backup(config, base, flags)

    def install(self, config, base, flags):
        for pkg in self.packages(base):
            self.logger.show(f"install flatpak {pkg!r}...")
            self.sh.exec(["flatpak", "install", "-y", "--or-updae", "--noninteractive", "flathub", pkg])

    def update(self, config, base, flags):
        for pkg in self.packages(base):
            self.logger.show(f"update flatpak {pkg!r}...")
            self.sh.exec(["flatpak", "update", "-y", "--noninteractive", "flathub", pkg])

    def backup(self, config, base, flags):
        self.logger.show("backup flatpak packages...")

        results = self.sh.exec(["flatpak", "list", "--app", "--columns=application"])
        lst = results.stdout.decode()
        with open(base, "w") as f:
            f.write(lst)
