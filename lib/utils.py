import os
import warnings

from xonsh.lazyasd import lazyobject


def add_PATH(*paths):
    for path in reversed(paths):
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            __xonsh__.env["PATH"].add(path, front=True)
        else:
            warnings.warn(f"{path} is not fould. skip adding to PATH")


def lazymodule(name):
    @lazyobject
    def module():
        import importlib
        return importlib.import_module(name)

    return module


class OneLineCache(object):
    def __init__(self, fn):
        self.i = None
        self.fn = fn
        self._cache = None

    def unwrap(self):
        i = len(__xonsh__.history)
        if self.i != i:
            self._cache = None

        if self._cache == None:
            self.i = i
            self._cache = self.fn()

        return self._cache

    def __iter__(self):
        return iter(self.unwrap())
