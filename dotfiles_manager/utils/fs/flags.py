from dotfiles_manager.utils.fs.base import DotfileFS
from dotfiles_manager.utils.fs.shell import InterfaceFS
from dotfiles_manager.utils.fs.utils import BaseClass
import copy


class Flags(BaseClass):
    def update(self, flags):
        return copy.deepcopy(flags)

    def __call__(self, fs: InterfaceFS, flags):
        new_flags = self.update(flags)
        super().__call(fs, new_flags)


class ForceYes(Flags):
    def update(self, flags):
        new_flags = super().update(flags)
        new_flags.y = True
        new_flags.n = False
        return new_flags
