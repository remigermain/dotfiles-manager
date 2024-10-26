import subprocess
import sys
from functools import wraps

PAT = ["permission denied", "superuser privileges"]


def need_superuser(text):
    text = text.lower()
    for match in PAT:
        if match in text:
            return True
    return False


@wraps(subprocess.run)
def run(cmds, sudo=True, showerror=True, **kw):
    kw.setdefault("text", True)
    kw.setdefault("shell", True)
    kw.setdefault("capture_output", True)

    cmds_str = " ".join(cmds)
    sudo_cmds_str = " ".join(["sudo"] + cmds)

    res = subprocess.run(cmds_str, **kw)
    if res.returncode == 0 or not sudo:
        return res

    res = subprocess.run(sudo_cmds_str, **kw)
    if res.returncode != 0 and showerror:
        print(res.stderr or res.stdout, file=sys.stderr)
    return res
