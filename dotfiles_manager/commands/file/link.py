import argparse
import stat
from pathlib import Path

from dotfiles_manager.commands.base import CommandAbstract, SubCommandAbstract
from dotfiles_manager.utils.utils import remove_list


class CommandLink(SubCommandAbstract):
    help = "synlik file"
    aliases = ("ln",)
    parent = "file"

    class Add(CommandAbstract):
        help = "add link file"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("files", nargs="+", type=Path, help="file needed to link")

        def handle(self, files: list[str], **option):
            files_config = self.config.get("link", [])
            for file in files:
                file = Path(file).expanduser().absolute()
                for actual, _ in files_config:
                    actual = Path(actual)
                    if actual == file:
                        self.stdout.write("file ", self.style.info(file), " already exists...")
                        break
                else:
                    file = file.resolve()
                    if self.config.fs.is_system_path(file):
                        if not self.stdout.warning.accept("symlink a file to your system can be break it?"):
                            continue

                    dest, is_user = self.config.fs.save(file)
                    self.config.fs.llink(dest, file)
                    self.stdout.write("linked ", self.style.info(dest))
                    files_config.append((file, dest))

            self.config.set("link", files_config)

    class Remove(CommandAbstract):
        help = "remove link file"
        aliases = ("rm",)

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("files", nargs="+", type=Path, help="file needed to remove")
            parser.add_argument("--no-remove", action="store_true", default=False, help="remove files")

        def handle(self, files, no_remove, **option):
            files_config = self.config.get("link", [])
            for file in files:
                file = Path(file).expanduser().absolute()
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
            self.config.set("link", files_config)

    class List(CommandAbstract):
        help = "list link files"
        aliases = ("ls",)

        def handle(self, **option):
            files = self.config.get("link", [])
            for source, _ in files:
                statsource = Path(source).expanduser().absolute().stat()

                ftype = "."
                if stat.S_ISDIR(statsource.st_mode):
                    ftype = "d"
                elif stat.S_ISREG(statsource.st_mode):
                    ftype = "f"
                self.stdout.write(f"{ftype} ", "->", self.style.info(source))

    class Update(CommandAbstract):
        help = "update link files"
        aliases = ("up",)

        def handle(self, **option):
            for dest, source in self.config.get("link", []):
                if self.config.fs.llink(source, dest):
                    self.stdout.write("linked ", self.style.info(dest))
                else:
                    self.stdout.write("already linked ", self.style.info(dest))
