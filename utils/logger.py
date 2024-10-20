import sys

from .singleton import Singleton


class Style(metaclass=Singleton):
    def __init__(self, **params):
        self._params = params

    def config(self, **params):
        self._params = params

    def _format(self, start, text, end):
        if self._params.get("color", True):
            return f"{start}{text}{end}"
        return text

    def info(self, text):
        return self._format("\33[94m", text, "\33[0m")

    def success(self, text):
        return self._format("\33[92m", text, "\33[0m")

    def error(self, text):
        return self._format("\33[91m", text, "\33[0m")

    def warning(self, text):
        return self._format("\33[93m", text, "\33[0m")

    def bold(self, text):
        return self._format("\33[1m", text, "\33[0m")

    def italic(self, text):
        return self._format("\33[3m", text, "\33[0m")

    def url(self, text):
        return self._format("\33[4m", text, "\33[0m")

    def blink(self, text):
        return self._format("\33[5m", text, "\33[0m")


class Method:
    def __init__(self, logger, color):
        self.logger = logger
        self._color = color

    def __call__(self, *ar: list[str]):
        self.logger.write(*[self._color(t) for t in ar])

    def input(self, *ar: list[str]):
        self(*ar)
        return input()

    def accept(self, *ar: list[str]):
        ar = [*ar]
        ar.append("[y/n]")
        self(*ar)
        return input().lower().strip() in ["y", "yes"]

    def choices(self, *ar: list[str], choices=None):
        shoices = ", ".join([f"{c}/{idx}" for idx, c in enumerate(choices, start=1)])
        self(*ar, shoices)
        res = input().lower().strip()
        if res in choices:
            return choices
        if res.isdigit() and int(res) <= len(choices):
            return choices[int(res)]

        self.logger.error("Invalid choices...\n")
        return self.choices(*ar, choices=choices)


class Logger:
    def __init__(self, stream=sys.stdout, style=None):
        self._stream = stream
        self._style = style or Style()
        self.info = Method(self, self._style.info)
        self.success = Method(self, self._style.success)
        self.warning = Method(self, self._style.warning)
        self.error = Method(self, self._style.error)

    def write(self, *arg: list[str]):
        """write texts"""
        self._stream.writelines([*arg, "\n"])
