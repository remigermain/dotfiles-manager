from collections.abc import Generator

from dotfiles_manager.utils.fs.fs import Copy, Delete, DotfileFS, File, Symlink
from dotfiles_manager.utils.fs.condition import Exists, IsDir, Condition
from dotfiles_manager.utils.fs.path import sanitize_source_path, EnumFile
from dotfiles_manager.utils.fs.flags import ForceYes
from dotfiles_manager.utils.fs.utils import Message
from dotfiles_manager.utils.config import DOTFILE_IGNORE_FOLDER
from dotfiles_manager.utils.style import style


def link_command(srcs, flags) -> Generator[DotfileFS]:
    for src in srcs:
        src, dest = sanitize_source_path(src, EnumFile.LINK)

        yield Exists(
            src,
            Copy(src, dest),
            IsDir(src, File(dest / DOTFILE_IGNORE_FOLDER)),
            ForceYes(Symlink(dest, src)),
        )


def unlink_command(srcs, flags) -> Generator[DotfileFS]:
    for src in srcs:
        src, dest = sanitize_source_path(src, EnumFile.LINK)

        yield Exists(
            src,
            Exists(
                dest,
                Delete(src),
                Copy(dest, src),
                Condition(not flags.no_remove, Delete(dest)),
            )
            | Message(
                f"'{style.error(dest)}' not already linked", is_error=True
            ),
        )
