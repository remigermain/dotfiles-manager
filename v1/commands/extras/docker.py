from .base import AbstractCommandElement
import os


class Docker(AbstractCommandElement):
    def exec(self, container, command):
        return self.sh.exec(["docker", "exec", container, self.sh.shlex(command)])

    def restart(self, container):
        return self.sh.exec(["docker", "restart", container])

    def id(self, container):
        return self.sh.exec(["docker", "ps", "-q", "-f", f"name={container}"])

    def rm(self, container):
        return self.sh.exec(["docker", "rm", "-f", container])


class DockerCompose(AbstractCommandElement):
    name = "docker_compose"

    def __init__(self, *ar, **kw):
        super().__init__(*ar, **kw)

        if not os.system("which docker-compose 2>/dev/null 1>/dev/null"):
            self.cmd = ["docker-compose"]
        else:
            self.cmd = ["docker", "compose"]

    def build(self, file, container=None):
        cmd = [*self.cmd, "-f", file, "build"]
        if container:
            cmd.append(container)
        return self.sh.exec(cmd)

    def up(self, file, container=None, build=False):
        cmd = [*self.cmd, "-f", file, "up", "-d"]
        if build:
            cmd.append("--build")
        if container:
            cmd.append(container)
        return self.sh.exec(cmd)
