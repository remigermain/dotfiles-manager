import sys
from collections.abc import Generator

from dotfiles_manager.utils.exception import InvalidDotfile, PermissionDotfile
from dotfiles_manager.utils.fs.fs import DotfileFS
from dotfiles_manager.utils.fs.shell import Shell


def runner(generator: Generator[DotfileFS], flags):
    as_error = False
    dots = []

    for dot in generator:
        fs = Shell(sudo=flags.sudo)
        dots.append((dot, fs))

        try:
            dot.validate(fs, flags)
        except InvalidDotfile as e:
            print(str(e), file=sys.stderr)
            as_error = True
        except PermissionDotfile:
            fs.sudo = True

    if as_error:
        exit(1)

    for dot, fs in dots:
        dot(fs, flags)
