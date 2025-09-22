import enum
import pathlib

from dotfiles_manager.utils.config import (
    OUTPUT_DOTFILE_HOME_COPY,
    OUTPUT_DOTFILE_HOME_LINK,
    OUTPUT_DOTFILE_SYSTEM_COPY,
    OUTPUT_DOTFILE_SYSTEM_LINK,
    OUTPUT_HOME,
)


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


def removeprefix(path: pathlib.Path, out_base: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(str(path).removeprefix(str(out_base) + "/"))
