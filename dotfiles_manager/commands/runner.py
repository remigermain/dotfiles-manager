import sys
from collections.abc import Generator

from dotfiles_manager.utils.exception import InvalidDotfile, PermissionDotfile
from dotfiles_manager.utils.fs.fs import DotfileFS
from dotfiles_manager.utils.fs.shell import Shell


def runner(generator: Generator[DotfileFS], flags):
    elements = list(generator)
    as_error = False
    need_sudo = []

    for el in elements:
        try:
            el.validate()
        except InvalidDotfile as e:
            print(str(e), file=sys.stderr)
            as_error = True
        except PermissionDotfile:
            need_sudo.append(el)

    if as_error:
        exit(1)

    for el in elements:
        fs = Shell()
        if el in need_sudo:
            fs.active_root()
        el(fs, flags)
