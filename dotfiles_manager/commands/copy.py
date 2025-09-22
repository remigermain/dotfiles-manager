from collections.abc import Generator

from dotfiles_manager.utils.fs.fs import Copy, DotfileFS, File
from dotfiles_manager.utils.fs.path import sanitize_source_path, EnumFile
from dotfiles_manager.utils.fs.condition import IsDir
from dotfiles_manager.utils.config import DOTFILE_IGNORE_FOLDER


def copy_command(srcs, flags) -> Generator[DotfileFS]:
    for src in srcs:
        src, dest = sanitize_source_path(src, EnumFile.COPY)

        yield Copy(src, dest)
        yield IsDir(src, File(dest / DOTFILE_IGNORE_FOLDER))
