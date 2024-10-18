import sys


class Style:
    def info(self, text):
        return f"\33[94m{text}\33[0m"

    def success(self, text):
        return f"\33[92m{text}\33[0m"

    def error(self, text):
        return f"\33[91m{text}\33[0m"

    def warning(self, text):
        return f"\33[93m{text}\33[0m"

    def bold(self, text):
        return f"\33[1m{text}\33[0m"

    def italic(self, text):
        return f"\33[3m{text}\33[0m"

    def url(self, text):
        return f"\33[4m{text}\33[0m"

    def blink(self, text):
        return f"\33[5m{text}\33[0m"


class Logger:
    def __init__(self, stream=sys.stdout):
        self._stream = stream
        self._style = Style()

    def write(self, *arg: list[str]):
        """write texts"""
        self._stream.writelines([*arg, "\n"])

    def info(self, *ar):
        self.write(*[self._style.info(t) for t in ar])

    def success(self, *ar):
        self.write(*[self._style.success(t) for t in ar])

    def error(self, *ar):
        self.write(*[self._style.error(t) for t in ar])
        return 1

    def warning(self, *ar):
        self.write(*[self._style.warning(t) for t in ar])

    def input(self, *ar):
        self.info(*ar)
        return input()
