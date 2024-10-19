import argparse
from pathlib import Path

from utils.conf import ConfigScope

from .base import CommandAbstract, SubCommandAbstract


class CommandCopy(SubCommandAbstract):
    help = "copy file"
    aliases = ("cp",)

    class Add(CommandAbstract):
        help = "add file"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("source", type=Path, help="file needed to copy")

        def handle(self, source, tags, **option):
            config = ConfigScope.from_name(CommandCopy.name)
            for actual, _ in config.get("files", []):
                actual = Path(actual)
                if actual == source:
                    self.stdout.write("file already exists...")
                    return

            dest, is_user = config.fs.save(source)
            config.add("files", (source, dest), **tags)
            self.stdout.write("copied ", self.style.info(source))

    class Remove(CommandAbstract):
        help = "remove file"
        aliases = ("rm",)

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("source", type=Path, help="file needed to remove")
            parser.add_argument("--no-remove", action="store_true", default=False, help="remove files")

        def handle(self, source, no_remove, **option):
            config = ConfigScope.from_name(CommandCopy.name)
            files = config.get("files", [])
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

            if not no_remove:
                config.fs.lremove(dest)
            self.stdout.write("file removed...")
            config.set("files", files)

    class List(CommandAbstract):
        help = "list files"
        aliases = ("ls",)

        def handle(self, **option):
            config = ConfigScope.from_name(CommandCopy.name)
            files = config.get("files", [])
            for source, dest in files:
                dest = config.fs.lpath(dest)
                self.stdout.write(source, self.style.info(self.style.bold(" -> ")), str(dest))

    class Update(CommandAbstract):
        help = "update files"
        aliases = ("up",)

        def handle(self, **option):
            config = ConfigScope.from_name(CommandCopy.name)
            files = config.get("files", [])
            for dest, source in files:
                is_same = config.fs.md5sum(dest) == config.fs.lmd5sum(source)
                if is_same:
                    self.stdout.write("already copied ", self.style.info(dest))
                    continue

                stat_dest = config.fs.stat(dest)
                stat_source = config.fs.lstat(source)
                if stat_dest.st_mtime > stat_source.st_mtime:
                    config.fs.save(dest)
                    self.stdout.write("copied from system ", self.style.info(dest))
                else:
                    config.fs.lcopy(source, dest)
                    self.stdout.write("copied from local ", self.style.info(dest))
