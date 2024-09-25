from .base import AbstractCommandElement


class Git(AbstractCommandElement):
    def pull(self, repository):
        return self.sh.exec(["git", "-C", repository, "pull"])

    def reset(self, repository):
        return self.sh.exec(["git", "reset", "--hard"])

    def clone(self, repository, output=None):
        cmds = ["git", "clone", "--recursive", repository]

        if output:
            cmds.append(output)

        return self.sh.exec(cmds)
