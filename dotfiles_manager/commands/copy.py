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

        yield Copy(src, dest) + File(dest / ".dot-folder")
