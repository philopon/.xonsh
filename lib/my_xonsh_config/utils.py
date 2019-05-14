import os
import warnings
from contextlib import contextmanager
import shutil
from functools import partial
from time import perf_counter
import resource

from xonsh.lazyasd import lazyobject


if __xonsh__.env.get("XONSH_INIT_BENCH"):
    @contextmanager
    def bench(name):
        start = perf_counter()
        yield
        end = perf_counter()
        print("{}: {}".format(name, end - start))
else:
    @contextmanager
    def bench(_name):
        yield


def alias(name_or_fn, name=None):
    if isinstance(name_or_fn, str):
        return partial(alias, name=name_or_fn)

    fn = name_or_fn
    name = fn.__name__ if name is None else name

    aliases[name] = fn
    return fn


def which(cmd, path=None):
    if path is None:
        path = ":".join(__xonsh__.env["PATH"])
    return shutil.which(cmd, path=path)


def add_PATH(*paths, warning=False):
    for path in reversed(paths):
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            __xonsh__.env["PATH"].add(path, front=True)
        else:
            if warning:
                warnings.warn("{} is not fould. skip adding to PATH".format(path))


def lazymodule(base_or_name, name=None):
    @lazyobject
    def module():
        import importlib
        if name is not None:
            return getattr(importlib.import_module(base_or_name), name)
        else:
            return importlib.import_module(base_or_name)

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


def _common_prefix2(a, b):
    a, b = (a, b) if len(a) > len(b) else (b, a)
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            return a[:i]

    return b


def common_prefix(cands):
    cands = iter(cands)
    try:
        p = next(cands)
    except StopIteration:
        return ""
    for cand in cands:
        p = _common_prefix2(p, cand)
        if len(p) == 0:
            return ""

    return p


@contextmanager
def workdir(wd):
    cwd = os.getcwd()
    os.chdir(wd)
    try:
        yield
    finally:
        os.chdir(cwd)


def relax_limit(rsc, threshold):
    soft, hard = resource.getrlimit(rsc)
    if soft < threshold:
        resource.setrlimit(rsc, (hard, hard))
