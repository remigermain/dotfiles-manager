import sys
from collections.abc import Generator

from dotfiles_manager.utils.exception import InvalidDotfile, PermissionDotfile
from dotfiles_manager.utils.fs.fs import DotfileFS
from dotfiles_manager.utils.fs.shell import Shell


def runner(generator: Generator[DotfileFS], flags):
    elements = list(generator)
    as_error = False
    need_superuser = []

    for el in elements:
        fs = Shell()
        try:
            el.validate(fs)
        except InvalidDotfile as e:
            print(str(e), file=sys.stderr)
            as_error = True
        except PermissionDotfile:
            need_superuser.append(el)

    if as_error:
        exit(1)

    for el in elements:
        fs = Shell()
        if el in need_superuser:
            fs.enable_superuser()
        el(fs, flags)
