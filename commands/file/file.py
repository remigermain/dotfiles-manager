from commands.base import SubCommandAbstract
from utils.utils import register_command

from .copy import CommandCopy
from .link import CommandLink


@register_command(CommandLink, CommandCopy)
class CommandFile(SubCommandAbstract):
    help = "manage files"
