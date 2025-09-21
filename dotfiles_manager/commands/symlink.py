from collections.abc import Generator

from dotfiles_manager.utils.fs.fs import (
    Copy,
    Delete,
    DotfileFS,
    EnumFile,
    File,
    Symlink,
    sanitize_source_path,
)


def link_command(srcs, flags) -> Generator[DotfileFS]:
    for src in srcs:
        src, dest = sanitize_source_path(src, EnumFile.LINK)

        cp = Copy(src, dest)
        # TODO permission
        if src.is_dir():
            cp += File(dest / ".dot-folder")
        cp += Symlink(dest, src, force_yes=True)
        yield cp


def unlink_command(srcs, flags) -> Generator[DotfileFS]:
    for src in srcs:
        src, dest = sanitize_source_path(src, EnumFile.LINK)

        delete = Delete(src)
        delete += Copy(dest, src)
        if not flags.no_remove:
            delete += Delete(dest)
        yield delete
