from pathlib import Path

from .base import CommandAbstract


class Link(CommandAbstract):
    description = "create linked files"

    def add_arguments(self, parser):
        sub = parser.add_subparsers(description="Available commands", dest="action", required=True)

        parser_add = sub.add_parser("add", help="add linked files")
        parser_add.add_argument("src", help="source files to add")

        parser_remove = sub.add_parser("remove", help="remove linked files")
        parser_remove.add_argument("src", help="source files to remove")

        parser_remove = sub.add_parser("update", help="update linked files")

    def run(self, config: dict, base: Path, flags):
        if flags.action == "update":
            self.update(config, base, flags)
            return

        flags.src = Path(flags.src)

        if flags.action == "add":
            self.add(config, base, flags)
        elif flags.action == "remove":
            self.remove(config, base, flags)

    def update(self, config, base, flags):
        refresh = False
        for el in config.linked:
            src = base / self.final_path(el["src"])
            dest = self.final_path(el["dest"])
            if not dest.is_symlink() or dest.resolve() != src:
                self.sh.rm(dest)
                self.sh.link(src, dest)
                self.logger.show(f"update missing link {str(el['dest'])!r}...")
                refresh = True
        if not refresh:
            self.logger.show("no files to link...")

    def add(self, config, base, flags):
        actual = {"src": flags.src, "dest": self.directory / flags.src.name}
        actual["src"] = self.sanitize_path(actual["src"])
        actual["dest"] = self.sanitize_path(actual["dest"])

        for el in config.linked:
            if self.final_path(actual["src"]) == self.final_path(el["dest"]):
                self.errx(f"destination {str(el['dest'])!r} already exists")

        self.sh.cp(actual["src"], base / actual["dest"])
        self.sh.rm(actual["src"])
        self.sh.link(base / actual["dest"], actual["src"])

        new = {"src": actual["dest"], "dest": actual["src"]}
        config.linked.append(new)

        self.logger.show(f"link {str(new['dest'])!r}...")

    def remove(self, config, base, flags):
        actual = {"src": flags.src, "dest": self.directory / flags.src.name}
        actual["src"] = self.sanitize_path(actual["src"])

        to_remove = []
        for el in config.linked:
            if self.final_path(actual["src"]) == self.final_path(el["dest"]):
                to_remove.append(el)

        if not to_remove:
            self.errx(f"link file {str(actual['src'])!r} dosen't exists...")

        for el in to_remove:
            self.sh.rm(Path(el["dest"]))
            self.sh.rm(base / Path(el["src"]))
            config.linked.remove(el)
            self.logger.show(f"unlink {str(el['dest'])!r}...")
