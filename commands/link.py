import argparse
from pathlib import Path

from utils.utils import remove_list

from .base import CommandAbstract, SubCommandAbstract


class CommandLink(SubCommandAbstract):
    help = "synlik file"
    aliases = ("ln",)

    class Add(CommandAbstract):
        help = "add link file"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("files", nargs="+", type=Path, help="file needed to link")

        def handle(self, files: list[str], **option):
            files_config = self.config.get("files", [])
            for file in files:
                for actual, _ in files_config:
                    actual = Path(actual)
                    if actual == file:
                        self.stdout.write("file ", self.style.info(file), " already exists...")
                        continue

                if self.config.fs.is_system_path(file):
                    if not self.stdout.warning.accept("symlink a file to your system can be break it?"):
                        continue

                dest, is_user = self.config.fs.save(file)
                self.config.fs.llink(dest, file)
                self.stdout.write("linked ", self.style.info(dest))
                files_config.append((file, dest))

            self.config.set("files", files_config)

    class Remove(CommandAbstract):
        help = "remove link file"
        aliases = ("rm",)

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("files", nargs="+", type=Path, help="file needed to remove")
            parser.add_argument("--no-remove", action="store_true", default=False, help="remove files")

        def handle(self, files, no_remove, **option):
            files_config = self.config.get("files", [])
            for file in files:
                for element in files_config:
                    actual = Path(element[0])
                    if actual == file:
                        break
                else:
                    self.stdout.write("file ", self.style.warning(file), " not found...")
                    continue

                source, dest = element
                files_config = remove_list(element, files_config)

                self.config.fs.lcopy(dest, source)
                if not no_remove:
                    self.config.fs.lremove(dest)
            self.config.set("files", files_config)

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
            for dest, source in self.config.get("files", []):
                if self.config.fs.llink(source, dest):
                    self.stdout.write("linked ", self.style.info(dest))
                else:
                    self.stdout.write("already linked ", self.style.info(dest))
