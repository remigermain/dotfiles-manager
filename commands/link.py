import argparse
from pathlib import Path

from utils.conf import ConfigScope

from .base import CommandAbstract, SubCommandAbstract


class CommandLink(SubCommandAbstract):
    name = "link"
    help = "synlik file"

    class Add(CommandAbstract):
        name = "add"
        help = "add link file"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("source", type=Path, help="file needed to link")

        def handle(self, source, tags, **option):
            config = ConfigScope.from_name(CommandLink.name)
            for element in config.get("files", []):
                actual = Path(element["content"][0])
                if actual == source:
                    self.stdout.write("file already exists...")
                    return

            dest, is_user = config.fs.save(source)
            tags = {"user": is_user, "system": not is_user} | tags
            config.add("files", (source, dest), **tags)
            config.save()

    class Remove(CommandAbstract):
        name = "rm"
        help = "remove link file"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("source", type=Path, help="file needed to remove")
            parser.add_argument("--no-remove", action="store_true", default=False, help="remove files")

        def handle(self, source, no_remove, **option):
            config = ConfigScope.from_name(CommandLink.name)
            files = config.get("files", [])
            for element in files:
                actual = Path(element["content"][0])
                if actual == source:
                    break
            else:
                self.stdout.write("file not found...")
                return

            idx = files.index(element)
            source, dest = element["content"]
            files = files[:idx] + files[idx + 1 :]

            config.fs.lcopy(dest, source)
            if not no_remove:
                config.fs.lremove(dest)
            config.set("files", files)
            config.save()

    class List(CommandAbstract):
        name = "list"
        help = "list link file"

        def handle(self, **option):
            config = ConfigScope.from_name(CommandLink.name)
            files = config.get("files", [])
            for element in files:
                source, dest = element["content"]
                dest = config.fs.lpath(dest)
                self.stdout.write(source, self.style.info(self.style.bold(" -> ")), str(dest))

    class Update(CommandAbstract):
        name = "update"
        help = "update link files"

        def handle(self, **option):
            config = ConfigScope.from_name(CommandLink.name)
            files = config.get("files", [])
            for element in files:
                dest, source = element["content"]

                if config.fs.llink(source, dest):
                    self.stdout.write("linked ", self.style.info(dest))
                else:
                    self.stdout.write("already linked ", self.style.info(dest))
