import subprocess
import sys

from dotfiles_manager.utils.config import DOTFILES_SCRIPTS


def script_command(script_name: str, flags) -> int:
    """functions to run script name in base dotfiles folders

    :param script_name: scirpt name (like: refresh, backup.py)
    :param flags: argv flags
    :return: return subprocess command
    """
    script = DOTFILES_SCRIPTS / script_name

    if not script.exists():
        sys.exit(f"{script_name} script don't exists")

    cmds = [script]
    if flags.no:
        cmds.append("-n")
    elif flags.yes:
        cmds.append("-y")

    if flags.sudo:
        cmds.insert(0, "sudo")

    args = getattr(flags, "*")
    if args is not None:
        cmds.extend(args)

    result = subprocess.run(cmds, cwd=DOTFILES_SCRIPTS)
    return result.returncode
