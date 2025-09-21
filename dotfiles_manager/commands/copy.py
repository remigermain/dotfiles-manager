from collections.abc import Generator

from dotfiles_manager.utils.fs.fs import (
    Copy,
    DotfileFS,
    EnumFile,
    File,
    sanitize_source_path,
)


def copy_command(srcs, flags) -> Generator[DotfileFS]:
    for src in srcs:
        src, dest = sanitize_source_path(src, EnumFile.COPY)

        cp = Copy(src, dest)
        if src.is_dir():
            cp += File(dest / ".dot-folder")
        yield cp
