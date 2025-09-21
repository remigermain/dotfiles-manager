class DotfileError(Exception):
    """BaseException dotfile"""


class PermissionDotfile(DotfileError):
    """Permission error if file/dir need root"""


class InvalidDotfile(DotfileError):
    """When dotfile file/dir dosent required spec"""
