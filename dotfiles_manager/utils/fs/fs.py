import enum
import mimetypes
import os
import pathlib

from dotfiles_manager.utils.config import (
    OUTPUT_DOTFILE_HOME_COPY,
    OUTPUT_DOTFILE_HOME_LINK,
    OUTPUT_DOTFILE_SYSTEM_COPY,
    OUTPUT_DOTFILE_SYSTEM_LINK,
    OUTPUT_HOME,
)
from dotfiles_manager.utils.exception import InvalidDotfile, PermissionDotfile
from dotfiles_manager.utils.fs.shell import InterfaceFS
from dotfiles_manager.utils.style import style
from dotfiles_manager.utils.template import template_file


def permission_safe(func):
    def _wraps(*ar, **kw):
        try:
            return func(*ar, **kw)
        except PermissionError as e:
            raise PermissionDotfile(f"Permission denied: {e}") from e

    return _wraps


class Permission:
    @staticmethod
    def check(src: pathlib.Path, mode: int) -> bool:
        for parent in src.expanduser().absolute().parents:
            try:
                if not parent.exists():
                    continue
            except PermissionError:
                return False
            return os.access(parent, mode)
        return False

    @staticmethod
    def read(src: pathlib.Path) -> bool:
        return Permission.check(src, os.R_OK)

    @staticmethod
    def write(src: pathlib.Path) -> bool:
        return Permission.check(src, os.W_OK)


class DotfileFS:
    def __init__(self, src, dest, force_yes=None):
        self.src = src
        self.dest = dest

        self.force_yes = force_yes

        self._next = None

    @permission_safe
    def validate(self):
        if not Permission.read(self.src):
            raise PermissionDotfile(
                f"Permission denied: '{style.error(str(self.src))}'"
            )
        if not Permission.write(self.dest):
            raise PermissionDotfile(
                f"Permission denied: '{style.error(str(self.dest))}'"
            )
        if not self.src.exists():
            raise InvalidDotfile(f"'{style.error(str(self.src))}' not exists")
        if not any((self.src.is_file(), self.src.is_dir())):
            raise InvalidDotfile(
                f"invalid type of file '{style.error(str(self.src))}'"
            )

    def __iadd__(self, element):
        if self._next is None:
            self._next = element
        else:
            self._next += element
        return self

    def __add__(self, element):
        self += element
        return self

    def next(self, *ar, **kw):
        if self._next:
            self._next(*ar, **kw)


class Copy(DotfileFS):
    @permission_safe
    def validate(self):
        super().validate()
        if self.src.resolve() == self.dest.resolve():
            raise InvalidDotfile(
                f"'{style.error(str(self.src))}' already linked"
            )

    def __call__(self, fs: InterfaceFS, flags):
        if self.src.is_file():
            fs.mkdir(self.src.parent)
            fs.copyfile(self.src, self.dest)
            print(f"copied file '{style.info(str(self.dest))}'")
        elif self.src.is_dir():
            fs.mkdir(self.src.parent)
            fs.copydir(self.src, self.dest)
            print(f"copied directory '{style.info(str(self.dest))}'")
        self.next(fs, flags)


class Symlink(DotfileFS):
    def __call__(self, fs: InterfaceFS, flags):
        if self.dest.exists():
            # same follow
            if self.dest.resolve() == self.src:
                print(
                    f"symlink already exists'{style.info(str(self.dest))}', \
                        ignore..."
                )
                return
            if flags.n:
                print(f"symlink '{style.info(str(self.dest))}' ignored...")
                return
            if not flags.y and self.force_yes is not True:
                if (
                    input(
                        f"'{style.info(str(self.dest))}' already exists, \
                            remove it ? [y/n]\n"
                    )
                    .strip()
                    .lower()
                    == "n"
                ):
                    return

        if self.src.is_file():
            fs.mkdir(self.src.parent)
            fs.symlinkfile(self.src, self.dest)
            print(f"symlink file '{style.info(str(self.dest))}'")
        elif self.src.is_dir():
            fs.mkdir(self.src.parent)
            fs.symlinkdir(self.src, self.dest)
            print(f"symlink directory '{style.info(str(self.dest))}'")
        self.next(fs, flags)


class Delete(DotfileFS):
    def __init__(self, src: pathlib.Path):
        super().__init__(src, src)

    def __call__(self, fs: InterfaceFS, flags):
        if self.src.is_file():
            fs.removefile(self.dest)
            print(f"delete file '{style.info(str(self.dest))}'")
        elif self.src.is_dir():
            fs.removedir(self.dest)
            print(f"delete directory' {style.info(str(self.dest))}'")

        self.next(fs, flags)


class File(DotfileFS):
    def __init__(self, src: pathlib.Path, content=""):
        super().__init__(src, src)
        self.content = content

    def __call__(self, fs: InterfaceFS, flags) -> None:
        fs.write(self.src, self.content)
        self.next()


class FileTemplate(File):
    def is_enable(self):
        """Run template only in textfile"""
        mine = mimetypes.guess_type(self.src)
        if mine[0] in ["text/plain", None]:
            return True
        return False

    def __call__(self, fs: InterfaceFS, flags) -> None:
        if not self.is_enable():
            return

        content = fs.read(self.src)
        # no change after templating, so ignore it
        if content == self.content:
            return
        self.content = template_file(content, flags)
        super().__call__(fs, flags)


class EnumFile(enum.IntEnum):
    COPY = enum.auto()
    LINK = enum.auto()


def sanitize_source_path(src: str, action: EnumFile) -> pathlib.Path:
    final = pathlib.Path(src).expanduser().absolute()
    home_prefix = str(OUTPUT_HOME) + "/"

    if str(final).startswith(str(home_prefix)):
        final = pathlib.Path(str(final).removeprefix(str(home_prefix)))
        output = (
            OUTPUT_DOTFILE_HOME_COPY
            if action == EnumFile.COPY
            else OUTPUT_DOTFILE_HOME_LINK
        )
    else:
        output = (
            OUTPUT_DOTFILE_SYSTEM_COPY
            if action == EnumFile.COPY
            else OUTPUT_DOTFILE_SYSTEM_LINK
        )

    dest = output / str(final).lstrip("/")
    return pathlib.Path(src), dest
