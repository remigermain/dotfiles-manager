import shlex
import subprocess
from pathlib import Path

from .base import AbstractCommandElement


class SH(AbstractCommandElement):
    def exec(self, command):
        cmds = [*self.shlex(command)]
        self.logger.info(f"sh exec: {cmds=}")
        res = subprocess.run(cmds, capture_output=True)

        if res.stderr:
            self.logger.warning(f"error response: {res.stderr!r}")
            raise Exception("Invalid return commands")

        return res

    def shlex(self, command):
        if isinstance(command, str):
            return shlex.split(command)
        elif not isinstance(command, (tuple, list)):
            command = [command]

        cmds = []
        for el in command:
            if isinstance(el, Path):
                el = el.expanduser()
            cmds.append(str(el))
        return cmds

    def mkdir(self, dir):
        return self.exec(["mkdir", "-p", dir])

    def rmdir(self, dir):
        return self.exec(["rmdir", "-rf", dir])

    def rm(self, element):
        return self.exec(["rm", "-rf", element])

    def untar(self, src, output):
        self.mkdir(output)
        return self.exec(["tar", "xf", src, "-D", output])

    def tar(self, name, src, *files):
        return self.exec(["tar", "cf", src, *files])

    def mv(self, src, dest):
        return self.exec(["mv", src, dest])

    def link(self, src, dest):
        return self.exec(["ln", "-s", src, dest])

    def cp(self, src, dest):
        return self.exec(["cp", src, dest])
