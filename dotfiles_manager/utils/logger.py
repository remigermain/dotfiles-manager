import logging
import sys


logger = logging.getLogger("dotfiles_manager")
stream = logging.StreamHandler(stream=sys.stdout)
stream.setFormatter(logging.Formatter("[%(name)s::%(levelname)s] %(message)s"))
logger.addHandler(stream)
