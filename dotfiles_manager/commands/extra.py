import subprocess

from dotfiles_manager.utils.config import BASE_DOTFILE


def refresh_command(flags):
    subprocess.run(["bash", "refresh.sh"], cwd=BASE_DOTFILE)


def backup_command(flags):
    cmds = ["bash", "backup.sh"]
    if flags.n:
        cmds.append("-n")
    elif flags.y:
        cmds.append("-y")
    subprocess.run(cmds, cwd=BASE_DOTFILE)
