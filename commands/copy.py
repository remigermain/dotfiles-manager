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
            parser.add_argument("source", type=Path, help="file needed to copy")

        def handle(self, source, **option):
            for actual, _ in self.config.get("files", []):
                actual = Path(actual)
                if actual == source:
                    self.stdout.write("file already exists...")
                    return

            dest, is_user = self.config.fs.save(source)
            self.config.add("files", (source, dest))
            self.stdout.write("copied ", self.style.info(source))

    class Remove(CommandAbstract):
        help = "remove file"
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

            source, dest = element
            files = remove_list(element, files)

            if not no_remove:
                self.config.fs.lremove(dest)
            self.stdout.write("file ", self.style.info(dest), "removed...")
            self.config.set("files", files)

    class List(CommandAbstract):
        help = "list files"
        aliases = ("ls",)

        def handle(self, **option):
            files = self.config.get("files", [])
            for source, dest in files:
                dest = self.config.fs.lpath(dest)
                self.stdout.write(source, self.style.info(self.style.bold(" -> ")), str(dest))

    class Update(CommandAbstract):
        help = "update files"
        aliases = ("up",)

        def handle(self, **option):
            files = self.config.get("files", [])
            for dest, source in files:
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
