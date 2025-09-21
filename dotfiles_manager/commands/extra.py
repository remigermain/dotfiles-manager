import subprocess
import sys

from dotfiles_manager.utils.config import BASE_DOTFILE


def refresh_command(flags):
    script = BASE_DOTFILE / "refresh.sh"
    if not script.exists():
        sys.exit("refresh.sh script don't exists")
    subprocess.run(["bash", "refresh.sh"], cwd=BASE_DOTFILE)


def backup_command(flags):
    script = BASE_DOTFILE / "backup.sh"
    if not script.exists():
        sys.exit("backup.sh script don't exists")

    cmds = ["bash", "backup.sh"]
    if flags.n:
        cmds.append("-n")
    elif flags.y:
        cmds.append("-y")
    subprocess.run(cmds, cwd=BASE_DOTFILE)
