import pathlib
from collections.abc import Generator
from itertools import chain

from dotfiles_manager.utils.config import (
    OUTPUT_DOTFILE_HOME_COPY,
    OUTPUT_DOTFILE_HOME_LINK,
    OUTPUT_DOTFILE_SYSTEM_COPY,
    OUTPUT_DOTFILE_SYSTEM_LINK,
    OUTPUT_HOME,
    OUTPUT_SYSTEM,
    DOTFILE_IGNORE_FOLDER,
)
from dotfiles_manager.utils.fs.condition import IsFile, Condition
from dotfiles_manager.utils.fs.path import removeprefix
from dotfiles_manager.utils.fs.log import Log
from dotfiles_manager.utils.fs.fs import Copy, Symlink, WriteFileTemplate
from dotfiles_manager.utils.style import style


def init_sub_command(
    src_path: pathlib.Path, dest_path: pathlib.Path
) -> Generator[(pathlib.Path, pathlib.Path)]:
    force_folders = [
        p.parent for p in src_path.glob(f"**/{DOTFILE_IGNORE_FOLDER}")
    ]
    already_generate = set()

    for source_file in src_path.glob("**"):
        # ignore folders
        if not source_file.is_file():
            continue

        for source_folder in force_folders:
            if str(source_file).startswith(str(source_folder)):
                if str(source_folder) not in already_generate:
                    already_generate.add(str(source_folder))
                    dest = dest_path / removeprefix(source_folder, src_path)
                    yield source_folder, dest
                break
        else:
            dest = dest_path / removeprefix(source_file, src_path)
            yield source_file, dest


def init_link_command(flags) -> Generator[Symlink]:
    gen = []
    if flags.only in (None, "home"):
        gen.append(init_sub_command(OUTPUT_DOTFILE_HOME_LINK, OUTPUT_HOME))
    if flags.only in (None, "system"):
        gen.append(init_sub_command(OUTPUT_DOTFILE_SYSTEM_LINK, OUTPUT_SYSTEM))

    for src, dest in chain(*gen):
        yield Condition(
            not flags.interactive or Log.Ask(f"synlink '{style.info(src)}' ?"),
            Symlink(src, dest),
            only_one=True,
        )


def init_copy_command(flags) -> Generator[Copy]:
    gen = []
    if flags.only in (None, "home"):
        gen.append(init_sub_command(OUTPUT_DOTFILE_HOME_COPY, OUTPUT_HOME))
    if flags.only in (None, "system"):
        gen.append(init_sub_command(OUTPUT_DOTFILE_SYSTEM_COPY, OUTPUT_SYSTEM))

    for src, dest in chain(*gen):
        yield Condition(
            not flags.interactive or Log.Ask(f"copy '{style.info(src)}' ?"),
            Copy(src, dest),
            IsFile(src, WriteFileTemplate(dest)),
            only_one=True,
        )


def init_command(flags) -> Generator[Symlink | Copy]:
    yield from init_link_command(flags)
    yield from init_copy_command(flags)
