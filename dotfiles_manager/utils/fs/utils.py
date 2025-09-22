from dotfiles_manager.utils.fs.base import BaseClass
from dotfiles_manager.utils.fs.fs import DotfileFS, InterfaceFS
import sys


class Message(BaseClass):
    def __init__(self, msg, *next: DotfileFS, is_error=False):
        super().__init__(*next)
        self.msg = msg
        self.is_error = is_error

    def __call__(self, fs: InterfaceFS, flags):
        print(self.msg, file=sys.stderr if self.is_error else sys.stdout)
        return super().__call__(fs, flags)
