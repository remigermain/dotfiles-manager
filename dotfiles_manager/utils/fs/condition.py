from codeop import CommandCompiler
import pathlib
from dotfiles_manager.utils.fs.base import DotfileFS
from dotfiles_manager.utils.fs.shell import InterfaceFS
from typing import Callable
from dotfiles_manager.utils.fs.utils import BaseClass


class Condition(BaseClass):
    def __init__(self, condition: bool | Callable, *next: DotfileFS):
        self.condition = condition
        self._or: Condition = None
        super().__init__(*next)

    def check_condition(self, fs: InterfaceFS):
        if callable(self.condition):
            return self.condition(fs)
        return bool(self.condition)

    def validate(self, fs: InterfaceFS):
        self.check_condition(fs)
        if self._or is not None:
            self._or.validate(fs)
        super().validate(fs)

    def __call__(self, fs: InterfaceFS, flags):
        if self.check_condition(fs):
            super().__call__(fs, flags)
        elif self._or is not None:
            self._or(fs, flags)

    def __or__(self, next):
        self._or = next
        return self


class IsDir(Condition):
    def __init__(self, src: pathlib.Path, *next: DotfileFS):
        condition = lambda fs: fs.is_dir(src)
        super().__init__(condition, *next)


class IsFile(Condition):
    def __init__(self, src: pathlib.Path, *next: DotfileFS):
        condition = lambda fs: fs.is_file(src)
        super().__init__(condition, *next)


class Exists(Condition):
    def __init__(self, src: pathlib.Path, *next: DotfileFS):
        condition = lambda fs: fs.exists(src)
        super().__init__(condition, *next)
