import subprocess

PAT = ["permission denied", "superuser privileges"]


def need_superuser(text):
    text = text.lower()
    for match in PAT:
        if match in text:
            return True
    return False


def run(cmds, **kw):
    kw.setdefault("capture_output", True)
    if not kw["capture_output"]:
        kw["stderr"] = subprocess.PIPE

    res = subprocess.run(cmds, **kw)
    if res.returncode == 0:
        return res.stdout

    err = res.stderr.decode()
    if need_superuser(err):
        cmds = ["sudo", *cmds]
        res = subprocess.run(cmds, **kw)

        if res.returncode == 0:
            return res.stdout
        err = res.stderr.decode()

    raise ValueError(err)
