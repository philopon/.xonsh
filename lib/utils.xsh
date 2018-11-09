import os
import warnings

from xonsh.lazyasd import lazyobject


def add_PATH(*paths):
    for path in reversed(paths):
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            $PATH.add(path, front=True)
        else:
            warnings.warn(f"{path} is not fould. skip adding to PATH")


def lazymodule(name):
    @lazyobject
    def module():
        import importlib
        return importlib.import_module(name)

    return module
