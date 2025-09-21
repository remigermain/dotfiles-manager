class Style:
    def __init__(self):
        self._flags = None

    def config(self, flags):
        self._flags = flags

    def _format(self, start, text, end):
        if not self._flags.no_color:
            return f"{start}{text}{end}"
        return str(text)

    def no(self, text):
        return str(text)

    def info(self, text):
        return self._format("\033[94m", text, "\033[0m")

    def success(self, text):
        return self._format("\033[92m", text, "\033[0m")

    def error(self, text):
        return self._format("\033[91m", text, "\033[0m")

    def warning(self, text):
        return self._format("\033[93m", text, "\033[0m")

    def bold(self, text):
        return self._format("\033[1m", text, "\033[0m")

    def italic(self, text):
        return self._format("\033[3m", text, "\033[0m")

    def url(self, text):
        return self._format("\033[4m", text, "\033[0m")

    def blink(self, text):
        return self._format("\033[5m", text, "\033[0m")


style = Style()
