import subprocess
import sys

from dotfiles_manager.utils.config import BASE_DOTFILE


def run_script(script_name: str, flags):
    script = BASE_DOTFILE / script_name
    if not script.exists():
        sys.exit(f"{script_name} script don't exists")

    cmds = ["bash", script_name]
    if flags.n:
        cmds.append("-n")
    elif flags.y:
        cmds.append("-y")
    subprocess.run(cmds, cwd=BASE_DOTFILE)


def refresh_command(flags):
    run_script("refresh.sh", flags)


def backup_command(flags):
    run_script("backup.sh", flags)
