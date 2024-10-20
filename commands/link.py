import argparse
from pathlib import Path

from utils.utils import is_root

from .base import CommandAbstract, SubCommandAbstract


class CommandLink(SubCommandAbstract):
    help = "synlik file"
    aliases = ("ln",)

    class Add(CommandAbstract):
        help = "add link file"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("source", type=Path, help="file needed to link")

        def handle(self, source, **option):
            for actual, _ in self.config.get("files", []):
                actual = Path(actual)
                if actual == source:
                    self.stdout.write("file already exists...")
                    return

            if self.config.fs.is_system_path(source):
                if not self.stdout.warning.accept("symlink a file to your system can be break it?"):
                    return
                if not is_root():
                    self.stdout.error("You are not root..")
                    return

            dest, is_user = self.config.fs.save(source)
            self.config.add("files", (source, dest))
            self.config.fs.llink(source, dest)
            self.stdout.write("linked ", self.style.info(dest))

    class Remove(CommandAbstract):
        help = "remove link file"
        aliases = ("rm",)

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("source", type=Path, help="file needed to remove")
            parser.add_argument("--no-remove", action="store_true", default=False, help="remove files")

        def handle(self, source, no_remove, **option):
            files = self.config.get("files", [])
            for element in files:
                actual = Path(element[0])
                if actual == source:
                    break
            else:
                self.stdout.write("file not found...")
                return

            idx = files.index(element)
            source, dest = element
            files = files[:idx] + files[idx + 1 :]

            self.config.fs.lcopy(dest, source)
            if not no_remove:
                self.config.fs.lremove(dest)
            self.config.set("files", files)

    class List(CommandAbstract):
        help = "list link files"
        aliases = ("ls",)

        def handle(self, **option):
            files = self.config.get("files", [])
            for source, dest in files:
                dest = self.config.fs.lpath(dest)
                self.stdout.write(source, self.style.info(self.style.bold(" -> ")), str(dest))

    class Update(CommandAbstract):
        help = "update link files"
        aliases = ("up",)

        def handle(self, **option):
            files = self.config.get("files", [])
            for dest, source in files:
                if self.config.fs.llink(source, dest):
                    self.stdout.write("linked ", self.style.info(dest))
                else:
                    self.stdout.write("already linked ", self.style.info(dest))
