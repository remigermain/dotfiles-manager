from dotfiles_manager.utils.exception import InvalidDotfile, PermissionDotfile
from dotfiles_manager.utils.fs.shell import InterfaceFS
from dotfiles_manager.utils.style import style
import abc


class DotfileInterface(abc.ABC):
    @abc.abstractmethod
    def validate(self, fs: InterfaceFS, flags):
        raise NotImplemented

    @abc.abstractmethod
    def __call__(self, fs: InterfaceFS, flags):
        raise NotImplemented


class DotfileFS(DotfileInterface):
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def validate(self, fs: InterfaceFS, flags):
        if not fs.exists(self.src):
            raise InvalidDotfile(f"'{style.error(str(self.src))}' not exists")
        if not any((fs.is_file(self.src), fs.is_dir(self.src))):
            raise InvalidDotfile(
                f"invalid type of file '{style.error(str(self.src))}'"
            )
        if not fs.can_read(self.src):
            raise PermissionDotfile(
                f"Permission denied: '{style.error(str(self.src))}'"
            )
        if not fs.can_write(self.dest):
            raise PermissionDotfile(
                f"Permission denied: '{style.error(str(self.dest))}'"
            )


class DotfileExtra(DotfileInterface):
    def __init__(self, *next: DotfileFS):
        self.next = next

    def validate(self, fs: InterfaceFS, flags):
        for next in self.next:
            next.validate(fs, flags)

    def __call__(self, fs: InterfaceFS, flags):
        for next in self.next:
            next(fs, flags)
