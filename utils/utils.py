import ast
import hashlib
import os


def md5sum(filename):
    h = hashlib.new("md5")
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(128 * h.block_size), b""):
            h.update(chunk)
    return h.hexdigest()


def is_root():
    return os.geteuid() == 0


def cast(value):
    try:
        return ast.literal_eval(value)
    except Exception:
        return value


def remove_list(element, lst):
    idx = lst.index(element)
    source, dest = element
    return lst[:idx] + lst[idx + 1 :]
