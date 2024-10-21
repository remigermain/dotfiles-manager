import argparse
from pathlib import Path

from utils.utils import remove_list

from .base import CommandAbstract, SubCommandAbstract


class CommandCopy(SubCommandAbstract):
    help = "copy file"
    aliases = ("cp",)

    class Add(CommandAbstract):
        help = "add file"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("file", dest="files", nargs="+", type=Path, help="file needed to copy")

        def handle(self, files: list[Path], **option):
            files_config = self.config.get("files", [])

            for file in files:
                for actual, _ in files_config:
                    actual = Path(actual)
                    if actual == file:
                        self.stdout.write("file ", self.style.warning(file), " already exists...")
                        continue

                dest, is_user = self.config.fs.save(file)
                files_config.append((file, dest))
                self.stdout.write("copied ", self.style.info(file))

            self.config.set("files", files_config)

    class Remove(CommandAbstract):
        help = "remove file"
        aliases = ("rm",)

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("file", nargs="+", dest="files", type=Path, help="file needed to remove")
            parser.add_argument("--no-remove", action="store_true", default=False, help="remove files")

        def handle(self, files: list[Path], no_remove: bool, **option):
            files_config = self.config.get("files", [])
            for file in files:
                for element in files:
                    actual = Path(element[0])
                    if actual == file:
                        break
                else:
                    self.stdout.write("file not found...")
                    continue
                source, dest = element
                files_config = remove_list(element, files_config)

                if not no_remove:
                    self.config.fs.lremove(dest)
                self.stdout.write("file ", self.style.info(dest), "removed...")

            self.config.set("files", files_config)

    class List(CommandAbstract):
        help = "list files"
        aliases = ("ls",)

        def handle(self, **option):
            for source, dest in self.config.get("files", []):
                dest = self.config.fs.lpath(dest)
                self.stdout.write(source, self.style.info(self.style.bold(" -> ")), str(dest))

    class Update(CommandAbstract):
        help = "update files"
        aliases = ("up",)

        def handle(self, **option):
            for dest, source in self.config.get("files", []):
                is_same = self.config.fs.md5sum(dest) == self.config.fs.lmd5sum(source)
                if is_same:
                    self.stdout.write("already copied ", self.style.info(dest))
                    continue

                stat_dest = self.config.fs.stat(dest)
                stat_source = self.config.fs.lstat(source)
                if stat_dest.st_mtime > stat_source.st_mtime:
                    self.config.fs.save(dest)
                    self.stdout.write("copied from system ", self.style.info(dest))
                else:
                    self.config.fs.lcopy(source, dest)
                    self.stdout.write("copied from local ", self.style.info(dest))
