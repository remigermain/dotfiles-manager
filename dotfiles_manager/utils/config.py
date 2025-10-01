import os
import pathlib
import sys
from collections import defaultdict

OUTPUT_HOME = pathlib.Path("~/").expanduser()
OUTPUT_SYSTEM = pathlib.Path("/").expanduser()
WHOAMI = os.getenv("USER")

BASE = OUTPUT_HOME / ".dotfile"
if not BASE.exists() or not BASE.is_file():
    sys.exit(f".dotfile for {WHOAMI!r} file is not defined")

BASE_DOTFILE = pathlib.Path(BASE.read_text().strip()).expanduser()

if not BASE_DOTFILE.exists() or not BASE_DOTFILE.is_dir():
    sys.exit(f"dotfile output '{str(BASE_DOTFILE)}' not exists")

OUTPUT_DOTFILE = BASE_DOTFILE / "files"

OUTPUT_DOTFILE_HOME_LINK = OUTPUT_DOTFILE / "home.link"
OUTPUT_DOTFILE_HOME_COPY = OUTPUT_DOTFILE / "home.copy"
OUTPUT_DOTFILE_SYSTEM_LINK = OUTPUT_DOTFILE / "system.link"
OUTPUT_DOTFILE_SYSTEM_COPY = OUTPUT_DOTFILE / "system.copy"

DOTFILES_SCRIPTS = BASE_DOTFILE / "scripts"

for out in (
    OUTPUT_DOTFILE_HOME_LINK,
    OUTPUT_DOTFILE_HOME_COPY,
    OUTPUT_DOTFILE_SYSTEM_LINK,
    OUTPUT_DOTFILE_SYSTEM_COPY,
):
    out.mkdir(parents=True, exist_ok=True)

DOTFILE_IGNORE_FOLDER = ".dot-folder"

MAP_SCRIPTS: dict[str, str] = {}
MAP_SCRIPTS_UNIQUE: set[str] = set()
_TMP_SCRIPTS = defaultdict(list)

for element in DOTFILES_SCRIPTS.glob("*.*"):
    if not element.is_file():
        continue
    _TMP_SCRIPTS[element.stem].append(element.name)

for name, scripts in _TMP_SCRIPTS.items():
    # if only one script add both name
    if len(scripts) == 1:
        MAP_SCRIPTS_UNIQUE.add(name)
        MAP_SCRIPTS[name] = scripts[0]
        MAP_SCRIPTS[scripts[0]] = scripts[0]
    else:
        for complete_name in scripts:
            MAP_SCRIPTS_UNIQUE.add(complete_name)
            MAP_SCRIPTS[complete_name] = complete_name

del _TMP_SCRIPTS
