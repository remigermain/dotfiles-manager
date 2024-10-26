import argparse
import configparser
import fnmatch
import io
import subprocess

from dotfiles_manager.commands.base import CommandAbstract, SubCommandAbstract
from dotfiles_manager.utils.shell import run
from dotfiles_manager.utils.utils import remove_list


class CommandDconf(SubCommandAbstract):
    help = "dconf integration"

    class Backup(CommandAbstract):
        help = "backup dconf"

        def handle(self, **option):
            self.stdout.write("backup ", self.style.info("dconf"), " settings...")

            res = run(["dconf", "dump", "/"])
            if not res:
                return self.stderr.error("invalid response from dconf...")

            dconf = self._sanitize(self.config, res.stdout)
            self.config.set("data", dconf)

        def _sanitize(self, config, dconf):
            file = io.StringIO(dconf)

            ignore_sections = config.get("ingore-sections", [])
            ignore_keys = config.get("ingore-keys", [])

            config = configparser.ConfigParser()
            config.read_file(file)

            deleted_sections = []
            deleted_section_keys = []
            for pattern in ignore_sections:
                for section in list(config.sections()):
                    if fnmatch.fnmatch(section, pattern):
                        deleted_sections.append(section)
                        del config[section]

            for section, keys in ignore_keys:
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

    class Ignore(CommandAbstract):
        help = "ignore sections"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("sections", nargs="+", help="ignore sections")

        def handle(self, sections, **options):
            sections = set(self.config.get("ingore-sections", [])) | set(sections)
            self.config.set("ingore-sections", list(sections))

    class IgnoreKey(CommandAbstract):
        help = "ignore sections keys"

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("section", help="ignore sections")
            parser.add_argument("key", help="ignore keys")

        def handle(self, section, key, **options):
            ik = self.config.get("ingore-keys", [])
            ik.append((section, key))
            self.config.set("ingore-keys", list(ik))

    class Remove(CommandAbstract):
        help = "remove sections"
        aliases = ("rm",)

        def add_arguments(self, parser: argparse.ArgumentParser):
            parser.add_argument("section", help="ignore sections")
            parser.add_argument("key", nargs="?", help="ignore keys")

        def handle(self, section, key=None, **options):
            if key:
                ik = self.config.get("ingore-keys", [])
                for element in ik:
                    k, v = element
                    if k == section and v == key:
                        self.config.set("ignore-keys", remove_list(element, ik))
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

    class Update(CommandAbstract):
        help = "load dconf"
        alias = ("load",)

        def handle(self, **option):
            self.stdout.write("load ", self.style.info("dconf"), " settings...")
            dconf = self.config.get("data", None)
            if not dconf:
                return

            stream = io.StringIO(dconf)
            if not run(["dconf", "load", "/"], stdin=stream):
                return self.stderr.error("invalid response from dconf...")
