from .base import SubCommandAbstract
from .fs.copy import CommandCopy
from .fs.link import CommandLink


class CommandFile(SubCommandAbstract):
    help = "manage files"

    CommandLink = CommandLink
    CommandCopy = CommandCopy
