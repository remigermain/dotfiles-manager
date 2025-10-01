import pathlib
from dotfiles_manager.utils.fs.base import DotfileFS
from dotfiles_manager.utils.fs.shell import InterfaceFS
from typing import Callable
from dotfiles_manager.utils.fs.base import DotfileExtra


class Condition(DotfileExtra):
    def __init__(
        self,
        condition: bool | Callable,
        *next: DotfileFS,
        only_one: bool = False,
    ):
        self.condition = condition
        self._or: Condition = None
        self._only_one = only_one
        self._mem_condition = None
        super().__init__(*next)

    def check_condition(self, fs: InterfaceFS, flags):
        if self._only_one and self._mem_condition is not None:
            return self._mem_condition

        if callable(self.condition):
            self._mem_condition = self.condition(fs, flags)
        else:
            self._mem_condition = bool(self.condition)

        return self._mem_condition

    def validate(self, fs: InterfaceFS, flags):
        self.check_condition(fs, flags)
        if self._or is not None:
            self._or.validate(fs, flags)
        super().validate(fs, flags)

    def __call__(self, fs: InterfaceFS, flags):
        if self.check_condition(fs, flags):
            super().__call__(fs, flags)
        elif self._or is not None:
            self._or(fs, flags)

    def __or__(self, next):
        self._or = next
        return self


class IsDir(Condition):
    def __init__(self, src: pathlib.Path, *next: DotfileFS):
        def condition(fs):
            return fs.is_dir(src)

        super().__init__(condition, *next)


class IsFile(Condition):
    def __init__(self, src: pathlib.Path, *next: DotfileFS):
        def condition(fs):
            return fs.is_file(src)

        super().__init__(condition, *next)


class Exists(Condition):
    def __init__(self, src: pathlib.Path, *next: DotfileFS):
        def condition(fs):
            return fs.exists(src)

        super().__init__(condition, *next)
