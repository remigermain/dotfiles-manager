import configparser
import fnmatch
import io
import subprocess

from commands.base import CommandAbstract, SubCommandAbstract
from utils.conf import ConfigScope
from utils.utils import remove_list


class CommandDconf(SubCommandAbstract):
    help = "flatpak integration"

    class Backup(CommandAbstract):
        help = "backup all deconf"

        def handle(self, **option):
            config = ConfigScope.from_name(CommandDconf.name)
            res = subprocess.run(["dconf", "dump", "/"], capture_output=True)
            if not res:
                self.stderr.error("Invalid response from  dconf")

            dconf = self._sanitize(config, res.stdout.decode())
            self.stdout.info("dconf backup...")
            config.set("data", dconf)

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
        help = "ignore"

        def add_arguments(self, parser):
            parser.add_argument("sections", nargs="+", help="ignore sections")

        def handle(self, sections, **options):
            config = ConfigScope.from_name(CommandDconf.name)

            sections = set(config.get("ingore-sections", [])) | set(sections)
            config.set("ingore-sections", list(sections))

    class IgnoreKey(CommandAbstract):
        help = "ignorekey"

        def add_arguments(self, parser):
            parser.add_argument("section", help="ignore sections")
            parser.add_argument("key", help="ignore keys")

        def handle(self, section, key, **options):
            config = ConfigScope.from_name(CommandDconf.name)

            ik = config.get("ingore-keys", [])
            ik.append((section, key))
            config.set("ingore-keys", list(ik))

    class Remove(CommandAbstract):
        help = "remove sections"

        def add_arguments(self, parser):
            parser.add_argument("section", help="ignore sections")
            parser.add_argument("key", nargs="?", help="ignore keys")

        def handle(self, section, key=None, **options):
            config = ConfigScope.from_name(CommandDconf.name)

            if key:
                ik = config.get("ingore-keys", [])
                for element in ik:
                    k, v = element
                    if k == section and v == key:
                        config.set("ignore-keys", remove_list(element, ik))
                        self.stdout.info(f"section {section!r} with key {key!r} removed")
                else:
                    self.stderr.error(f"no found section {section!r} or key {key!r}")
                return

            sec = config.get("ingore-sections", [])
            for element in sec:
                if element == section:
                    config.set("ignore-sections", remove_list(element, ik))
                    self.stdout.info(f"section {section!r} removed")
            else:
                self.stderr.error(f"no found section {section!r}")

    class Update(CommandAbstract):
        help = "update all donc"

        def handle(self, **option):
            config = ConfigScope.from_name(CommandDconf.name)
            dconf = config.get("data", None)
            if not dconf:
                return

            stream = io.StringIO(dconf)
            subprocess.run(["dconf", "load", "/"], stdin=stream)
            self.stdout.info("dconf loaded...")
