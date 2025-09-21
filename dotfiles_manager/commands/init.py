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
)
from dotfiles_manager.utils.fs.fs import Copy, FileTemplate, Symlink


def removeprefix(path: pathlib.Path, out_base: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(str(path).removeprefix(str(out_base) + "/"))


def init_sub_command(
    src_path: pathlib.Path, dest_path: pathlib.Path
) -> Generator[(pathlib.Path, pathlib.Path)]:
    force_folders = [p.parent for p in src_path.glob("**/.dot-folder")]
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
        yield Symlink(src, dest)


def init_copy_command(flags) -> Generator[Copy]:
    gen = []
    print(flags)
    if flags.only in (None, "home"):
        gen.append(init_sub_command(OUTPUT_DOTFILE_HOME_COPY, OUTPUT_HOME))
    if flags.only in (None, "system"):
        gen.append(init_sub_command(OUTPUT_DOTFILE_SYSTEM_COPY, OUTPUT_SYSTEM))

    for src, dest in chain(*gen):
        yield Copy(src, dest) + FileTemplate(dest)


def init_command(flags) -> Generator[Symlink | Copy]:
    yield from init_link_command()
    yield from init_copy_command()
