import importlib
import platform
import os

def pip(pkg, pyname=None):
    if not importlib.util.find_spec(pyname or pkg):
        xpip install @(pkg)

def fzf(base):
    bin = os.path.join(base, "bin", "fzf")
    if not os.path.isfile(bin):
        installer = os.path.join(base, "install-fzf")
        curl -L -o @(installer) https://raw.githubusercontent.com/junegunn/fzf/master/install
        bash @(installer) --bin
        os.remove(installer)

    return bin