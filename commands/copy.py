from pathlib import Path

from .base import CommandAbstract


class Copy(CommandAbstract):
    description = "copy files"

    def add_arguments(self, parser):
        sub = parser.add_subparsers(description="Available commands", dest="action", required=True)

        parser_add = sub.add_parser("add", help="add copy files")
        parser_add.add_argument("src", help="source files to add")

        parser_remove = sub.add_parser("remove", help="remove copy files")
        parser_remove.add_argument("src", help="source files to remove")

        parser_update = sub.add_parser("update", help="update copy files")
        parser_backup = sub.add_parser("backup", help="backup copy files")

    def run(self, config: dict, base: Path, flags):
        if flags.action in ("update", "backup"):
            self.update(config, base, flags)
            return

        flags.src = Path(flags.src)

        if flags.action == "add":
            self.add(config, base, flags)
        elif flags.action == "remove":
            self.remove(config, base, flags)

    def hash_file(self, path):
        import hashlib

        BLOCKSIZE = 65536
        hasher = hashlib.md5()
        with open(path, "rb") as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        return hasher.hexdigest()

    def update(self, config, base, flags):
        refresh = False
        for el in config.copies:
            src = self.final_path(base / self.final_path(el["src"]))
            dest = self.final_path(el["dest"])

            src_mtime = src.stat().st_mtime
            dest_mtime = dest.stat().st_mtime
            if dest_mtime > src_mtime:
                self.sh.cp(dest, src)
                self.logger.show(f"update system file {str(dest)!r}...")
                refresh = True
                continue

            src_hash = self.hash_file(src)
            dest_hash = self.hash_file(dest)
            if src_hash != dest_hash:
                self.sh.cp(src, dest)
                self.logger.show(f"update local file {str(dest)!r}...")
                refresh = True

        if not refresh:
            self.logger.show("no files to copy...")

    def add(self, config, base, flags):
        actual = {"src": flags.src, "dest": self.directory / flags.src.name}
        actual["src"] = self.sanitize_path(actual["src"])
        actual["dest"] = self.sanitize_path(actual["dest"])

        for el in config.copies:
            if self.final_path(actual["src"]) == self.final_path(el["dest"]):
                self.errx(f"destination {str(el['dest'])!r} already exists")

        self.sh.cp(actual["src"], base / actual["dest"])

        new = {"src": actual["dest"], "dest": actual["src"]}
        config.copies.append(new)

        self.logger.show(f"copy {str(new['dest'])!r}...")

    def remove(self, config, base, flags):
        actual = {"src": flags.src, "dest": self.directory / flags.src.name}
        actual["src"] = self.sanitize_path(actual["src"])

        to_remove = []
        for el in config.copies:
            if self.final_path(actual["src"]) == self.final_path(el["dest"]):
                to_remove.append(el)

        if not to_remove:
            self.errx(f"copy file {str(actual['src'])!r} dosen't exists...")

        for el in to_remove:
            self.sh.rm(base / Path(el["src"]))
            config.copies.remove(el)
            self.logger.show(f"remove {str(el['dest'])!r}...")
