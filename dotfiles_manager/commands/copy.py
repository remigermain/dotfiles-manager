from collections.abc import Generator

from dotfiles_manager.utils.fs.fs import Copy, DotfileFS, File, Chown
from dotfiles_manager.utils.fs.path import sanitize_source_path, EnumFile
from dotfiles_manager.utils.fs.condition import IsDir, Exists
from dotfiles_manager.utils.fs.utils import Message
from dotfiles_manager.utils.config import DOTFILE_IGNORE_FOLDER, WHOAMI
from dotfiles_manager.utils.style import style


def copy_command(srcs, flags) -> Generator[DotfileFS]:
    for src in srcs:
        src, dest = sanitize_source_path(src, EnumFile.COPY)

        yield Exists(
            src,
            Copy(src, dest),
            Chown(dest, WHOAMI),
            IsDir(src, File(dest / DOTFILE_IGNORE_FOLDER)),
        ) | Message(f"'{style.error(src)}' not exists")
