from collections.abc import Generator

from dotfiles_manager.utils.fs.fs import (
    Copy,
    Delete,
    DotfileFS,
    WriteFile,
    Symlink,
    Chown,
)
from dotfiles_manager.utils.fs.condition import Exists, IsDir, Condition
from dotfiles_manager.utils.fs.path import sanitize_source_path, EnumFile
from dotfiles_manager.utils.fs.flags import ForceYes
from dotfiles_manager.utils.config import DOTFILE_IGNORE_FOLDER, WHOAMI
from dotfiles_manager.utils.style import style
from dotfiles_manager.utils.fs.log import Log


def link_command(srcs, flags) -> Generator[DotfileFS]:
    for src in srcs:
        src, dest = sanitize_source_path(src, EnumFile.LINK)

        yield Exists(
            src,
            Copy(src, dest),
            IsDir(src, WriteFile(dest / DOTFILE_IGNORE_FOLDER)),
            Chown(dest, WHOAMI),
            ForceYes(Symlink(dest, src)),
        ) | Log.Error(f"'{style.error(src)}' not exists")


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
            | Log.Error(f"'{style.error(dest)}' not already linked"),
        ) | Log.Error(f"'{style.error(src)}' not exists")
