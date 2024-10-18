RESERVED = dir(dict)


class DictProxy(dict):
    def __init__(self, original):
        self.__original = original
        super().__init__(original)

    def setdefault(self, key, default):
        self.__original.setdefault(key, default)
        super().setdefault(key, default)

    def __getattribute__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError:
            self.__original.setdefault(key, {})
            return convert_nested_items(self.__original[key])

    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self[name] = value

    def __iter__(self):
        for el in self.__original:
            yield convert_nested_items(el)

    def __getitem__(self, k):
        return convert_nested_items(super().__getitem__(k))

    def __setitem__(self, k, v):
        self.__original[k] = v
        super().__setitem__(k, v)

    def __delitem__(self, k):
        del self.__original[k]
        super().__delitem__(k)

    def __delattr__(self, attr):
        del self[attr]


class ListProxy(list):
    def __init__(self, original):
        self.__original = original
        super().__init__(original)

    def __getitem__(self, k):
        return convert_nested_items(super().__getitem__(k))

    def __iter__(self):
        for el in self.__original:
            yield convert_nested_items(el)

    def __setitem__(self, k, v):
        self.__original[k] = v
        super().__setitem__(k, v)

    def append(self, *ar, **kw):
        self.__original.append(*ar, **kw)
        return super().append(*ar, **kw)

    def remove(self, *ar, **kw):
        self.__original.remove(*ar, **kw)
        return super().remove(*ar, **kw)

    def extend(self, *ar, **kw):
        self.__original.extend(*ar, **kw)
        return super().extend(*ar, **kw)


class TupleProxy(tuple):
    def __init__(self, original):
        self.__original = original
        super().__init__(original)

    def __new__(cls, original):
        return super().__new__(tuple, original)

    def __getitem__(self, k):
        return convert_nested_items(super().__getitem__(k))


def convert_nested_items(item):
    if isinstance(item, dict):
        return DictProxy(item)
    if isinstance(item, list):
        return ListProxy(item)
    return item
