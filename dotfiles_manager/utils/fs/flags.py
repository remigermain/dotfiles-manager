from dotfiles_manager.utils.fs.base import BaseClass
from dotfiles_manager.utils.fs.shell import InterfaceFS
import copy


class Flags(BaseClass):
    def update(self, flags):
        return copy.deepcopy(flags)

    def __call__(self, fs: InterfaceFS, flags):
        new_flags = self.update(flags)
        super().__call__(fs, new_flags)


class ForceYes(Flags):
    def update(self, flags):
        new_flags = super().update(flags)
        new_flags.y = True
        new_flags.n = False
        return new_flags
