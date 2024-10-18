import abc


class AbstractCommandElement(abc.ABC):
    def __init__(self, logger, parent):
        self.__parent = parent
        self.logger = logger
        if not hasattr(self, "name"):
            self.name = self.__class__.__name__.lower()

    def __getattribute__(self, attr):
        try:
            return super().__getattribute__(attr)
        except AttributeError:
            return getattr(self.__parent, attr)
