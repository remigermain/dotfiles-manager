import abc
import io
import pathlib
import subprocess
import tempfile


class InterfaceFS(abc.ABC):
    @abc.abstractmethod
    def mkdir(self, path: pathlib.Path): ...

    @abc.abstractmethod
    def copyfile(self, src: pathlib.Path, dest: pathlib.Path): ...

    @abc.abstractmethod
    def copydir(self, src: pathlib.Path, dest: pathlib.Path): ...

    @abc.abstractmethod
    def symlinkfile(self, src: pathlib.Path, dest: pathlib.Path): ...

    @abc.abstractmethod
    def symlinkdir(self, src: pathlib.Path, dest: pathlib.Path): ...

    @abc.abstractmethod
    def removefile(self, path: pathlib.Path): ...

    @abc.abstractmethod
    def removedir(self, path: pathlib.Path): ...

    @abc.abstractmethod
    def write(self, path: pathlib.Path, content: str | bytes): ...

    @abc.abstractmethod
    def read(self, path: pathlib.Path): ...


class Shell(InterfaceFS):
    def __init__(self):
        self._root = False

    def active_root(self):
        self._root = True

    def run(self, cmds, *ar, **kw):
        kw.setdefault("stdout", subprocess.PIPE)
        kw.setdefault("stderr", subprocess.PIPE)
        cmds = list(cmds)
        if self._root:
            cmds.insert(0, "sudo")

        result = subprocess.run(cmds, **kw)
        result.check_returncode()
        return result

    def mkdir(self, path: pathlib.Path):
        self.run(["mkdir", "-p", str(path)])

    def copyfile(self, src: pathlib.Path, dest: pathlib.Path):
        self.run(["cp", str(src), str(dest)])

    def copydir(self, src: pathlib.Path, dest: pathlib.Path):
        self.run(["cp", "-r", str(src), str(dest)])

    def symlinkfile(self, src: pathlib.Path, dest: pathlib.Path):
        self.run(["ln", "-f", "-s", str(src), str(dest)])

    def symlinkdir(self, src: pathlib.Path, dest: pathlib.Path):
        self.symlinkfile(src, dest)

    def removefile(self, path: pathlib.Path):
        self.run(["rm", "-f", str(path)])

    def removedir(self, path: pathlib.Path):
        self.run(["rm", "-rf", str(path)])

    def write(
        self,
        path: pathlib.Path,
        content: str | bytes | io.StringIO | io.BytesIO,
    ):
        if not isinstance(content, (io.StringIO | io.BytesIO)):
            if isinstance(content, str):
                stdin = io.StringIO()
            else:
                stdin = io.BytesIO()
            stdin.write(content)
            stdin.seek(0)
        else:
            stdin = content

        # create a temporyfile to copy to its final dest
        with tempfile.NamedTemporaryFile() as f:
            f.write(stdin.read().encode())
            f.seek(0)
            self.copyfile(f.name, str(path))

    def read(self, path: pathlib.Path) -> str:
        result = self.run(["cat", str(path)])
        return result.stdout.decode()
