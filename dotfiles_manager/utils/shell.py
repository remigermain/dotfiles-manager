import re
import subprocess
import sys
from functools import wraps

SPACE = re.compile(r"\s")


@wraps(subprocess.run)
def run(cmds, sudo=True, showerror=True, **kw):
    kw.setdefault("text", True)
    kw.setdefault("shell", True)
    kw.setdefault("capture_output", True)

    # escape space with string
    newcmds = []
    for cm in cmds:
        if SPACE.search(cm):
            cm = cm.replace('"', '\\"')
            cm = f'"{cm}"'
        newcmds.append(cm)

    cmds_str = " ".join(newcmds)
    sudo_cmds_str = " ".join(["sudo"] + newcmds)

    res = subprocess.run(cmds_str, **kw)
    if res.returncode == 0 or not sudo:
        return res

    res = subprocess.run(sudo_cmds_str, **kw)
    if res.returncode != 0 and showerror:
        print(res.stderr or res.stdout, file=sys.stderr)
    return res
