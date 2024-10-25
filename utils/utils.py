import ast
import hashlib
from typing import Any


def md5sum(filename) -> str:
    h = hashlib.new("md5")
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(128 * h.block_size), b""):
            h.update(chunk)
    return h.hexdigest()


def cast(value) -> Any:
    try:
        return ast.literal_eval(value)
    except Exception:
        return value


def remove_list[T](element: T, lst: list[T]) -> list[T]:
    idx = lst.index(element)
    return lst[:idx] + lst[idx + 1 :]


def register_command(*commands):
    def _wraps(_cls):
        for command in commands:
            setattr(_cls, command.__name__, command)
        return _cls

    return _wraps
