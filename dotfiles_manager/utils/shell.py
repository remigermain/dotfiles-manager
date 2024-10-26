import subprocess

PAT = ["permission denied", "superuser privileges"]


def need_superuser(text):
    text = text.lower()
    for match in PAT:
        if match in text:
            return True
    return False


def run(cmds, **kw):
    cmds_str = " ".join(cmds)
    sudo_cmds_str = " ".join(["sudo"] + cmds)

    res = subprocess.run(cmds_str, text=True, shell=True, capture_output=True)
    if res.returncode == 0:
        return res

    res = subprocess.run(sudo_cmds_str, text=True, shell=True, capture_output=True)
    if res.returncode != 0:
        print(res.stderr or res.stdout, file=sys.stderr)
    return res
