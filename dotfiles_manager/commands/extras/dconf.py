import argparse
import configparser
import fnmatch
import io
from tempfile import NamedTemporaryFile

from dotfiles_manager.commands.base import CommandAbstract, SubCommandAbstract, command
from dotfiles_manager.utils.shell import run
from dotfiles_manager.utils.utils import remove_list


class CommandDconf(SubCommandAbstract):
    help = "dconf integration"

    @command(help="backup dconf")
    def backup(self, **option):
        self.stdout.write("backup ", self.style.info("dconf"), " settings...")

        res = run(["dconf", "dump", "/"])
        if not res:
            return self.stderr.error("invalid response from dconf...")

        with NamedTemporaryFile("w", suffix=".ini") as f:
            f.write(self._sanitize(self.config, res.stdout))
            self.config.fs.copy(f.name, self.config.fs.lbase("dconf.ini"))

    def _sanitize(self, config, dconf):
        file = io.StringIO(dconf)

        ignore_sections = config.get("ingore-sections", [])
        ignore_keys = config.get("ingore-keys", {})

        config = configparser.ConfigParser()
        config.read_file(file)

        deleted_sections = []
        deleted_section_keys = []
        for pattern in ignore_sections:
            for section in list(config.sections()):
                if fnmatch.fnmatch(section, pattern):
                    deleted_sections.append(section)
                    del config[section]

        for section, keys in ignore_keys.items():
            if section not in list(config.sections()):
                continue
            info = config[section]
            for k in keys:
                if k in info:
                    deleted_section_keys.append((section, k))
                    del info[k]

        output = io.StringIO()
        config.write(output)
        output.seek(0)
        return output.read()

    @command(help="load dconf", aliases=("load",))
    def update(self, **option):
        if not self.config.fs.exist(self.config.fs.lbase("dconf.ini")):
            return self.stdout.write("no config docnf.ini...")

        self.stdout.write("load ", self.style.info("dconf"), " settings...")
        with self.config.fs.lbase("dconf.ini").open("r") as f:
            if not run(["dconf", "load", "/"], stdin=f):
                return self.stderr.error("invalid response from dconf...")

    class Ignore(CommandAbstract):
        help = "ignore sections"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("sections", nargs="+", help="ignore sections")

        def handle(self, sections, **options):
            sections = set(self.config.get("ingore-sections", [])) | set(sections)
            self.config.set("ingore-sections", sorted(sections))

    class IgnoreKey(CommandAbstract):
        help = "ignore sections keys"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("section", help="ignore sections")
            parser.add_argument("key", nargs="+", help="ignore keys")

        def handle(self, section, keys, **options):
            ik = self.config.get("ingore-keys", {})
            ackey = ik.setdefault(section, [])
            ackey.extends(keys)
            ik[section] = sorted(set(ackey))
            self.config.set("ingore-keys", ik)

    class Remove(CommandAbstract):
        help = "remove sections"
        aliases = ("rm",)

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("section", help="ignore sections")
            parser.add_argument("key", nargs="?", help="ignore keys")

        def handle(self, section, key=None, **options):
            if key:
                ik = self.config.get("ingore-keys", {})
                for k, v in ik.items():
                    if k == section and key in v:
                        self.config.set("ignore-keys", remove_list(v, ik))
                        self.stdout.write(
                            "section ", self.style.info(section), " with key ", self.style.info(key), " removed"
                        )
                else:
                    self.stderr.write("no found section ", self.style.error(section), " or key ", self.style.error(key))
                return

            sec = self.config.get("ingore-sections", [])
            for element in sec:
                if element == section:
                    self.config.set("ignore-sections", remove_list(element, ik))
                    self.stderr.write("section ", self.style.info(section), " removed")
            else:
                self.stderr.write("no found section ", self.style.error(section))
