from dotfiles_manager.utils.fs.base import DotfileExtra
from dotfiles_manager.utils.fs.shell import InterfaceFS
import copy


class Flags(DotfileExtra):
    def update(self, flags):
        return copy.deepcopy(flags)

    def __call__(self, fs: InterfaceFS, flags):
        new_flags = self.update(flags)
        super().__call__(fs, new_flags)


class ForceYes(Flags):
    def update(self, flags):
        new_flags = super().update(flags)
        new_flags.yes = True
        new_flags.no = False
        return new_flags
