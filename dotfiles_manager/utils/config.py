import os
import pathlib
import sys

OUTPUT_HOME = pathlib.Path("~/").expanduser()
OUTPUT_SYSTEM = pathlib.Path("/").expanduser()

BASE = OUTPUT_HOME / ".dotfile"
if not BASE.exists() or not BASE.is_file():
    whoami = os.getenv("USER")
    sys.exit(f".dotfile for {whoami!r} file is not defined")

BASE_DOTFILE = pathlib.Path(BASE.read_text().strip()).expanduser()

if not BASE_DOTFILE.exists() or not BASE_DOTFILE.is_dir():
    sys.exit(f"dotfile output '{str(BASE_DOTFILE)}' not exists")

OUTPUT_DOTFILE = BASE_DOTFILE / "files"

OUTPUT_DOTFILE_HOME_LINK = OUTPUT_DOTFILE / "home.link"
OUTPUT_DOTFILE_HOME_COPY = OUTPUT_DOTFILE / "home.copy"
OUTPUT_DOTFILE_SYSTEM_LINK = OUTPUT_DOTFILE / "system.link"
OUTPUT_DOTFILE_SYSTEM_COPY = OUTPUT_DOTFILE / "system.copy"

for out in (
    OUTPUT_DOTFILE_HOME_LINK,
    OUTPUT_DOTFILE_HOME_COPY,
    OUTPUT_DOTFILE_SYSTEM_LINK,
    OUTPUT_DOTFILE_SYSTEM_COPY,
):
    out.mkdir(parents=True, exist_ok=True)
