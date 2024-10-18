import argparse
from pathlib import Path

from utils.config import DotfileRC
from utils.utils import hashs

from .base import CommandAbstract, SubCommandAbstract


class CommandLink(SubCommandAbstract):
    name = "link"
    help = "synlik file"

    class Add(CommandAbstract):
        name = "add"
        help = "add link file"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("source", type=Path, help="file needed to link")

        def handle(self, source, **option):
            data = DotfileRC.Data()
            data.setdefault(CommandLink.name, [])
            for _, d in data[CommandLink.name]:
                if Path(d).expanduser() == source:
                    self.stdout.write("file already exists...")
                    return

            with data.files(CommandLink.name) as link:
                dest = link.save(source)
                link.link(dest, source)
                data[CommandLink.name].append((str(dest), str(source)))
            data.save()

    class Remove(CommandAbstract):
        name = "rm"
        help = "remove link file"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("source", type=Path, help="file needed to remove")

        def handle(self, source, **option):
            data = DotfileRC.Data()
            data.setdefault(CommandLink.name, [])

            for element in data[CommandLink.name]:
                _, d = element
                if Path(d).expanduser() == source:
                    break
            else:
                return self.stdout.error("file not found...")

            # remove it
            source, dest = element
            data[CommandLink] = [e for e in data[CommandLink.name] if e is not element]

            with data.files(CommandLink.name) as link:
                link.copyfile(source, dest)
                link.delete(source)
            data.save()
