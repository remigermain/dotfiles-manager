from pathlib import Path

from .base import CommandAbstract


class Packages(CommandAbstract):
    name = "pkg"
    description = "install pkgs"

    def run(self, config, base, flags):
        base = base / Path("packages")
        base.mkdir(parents=True, exist_ok=True)

        self.logger.show("upgrade pip...")
        self.sh.exec(["python3", "-m", "pip", "install", "--upgrade", "pip"])
        requirements = base / "requirements.txt"
        if requirements.exists():
            self.logger.show("upgrade python packages...")
            self.sh.exec(["python3", "-m", "pip", "install", "-r", requirements])

        self.logger.show("install npm...")
        self.sh.exec(["npm", "i"])

        flatpak = base / "flatpak.txt"
        if flatpak.exists():
            apps = [f.strip() for f in flatpak.open().readlines() if f.strip()]
            self.logger.show("install flatpak...")
            self.sh.exec(["flatpak", "install", "-y", "--or-update", "--noninteractive", "flathub", *apps])
