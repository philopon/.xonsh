import importlib
import platform
import os
import zipfile
from io import BytesIO

def pip(pkg, pyname=None):
    if not importlib.util.find_spec(pyname or pkg):
        xpip install @(pkg)


def fzf(base):
    bin = os.path.join(base, "bin", "fzf")
    if os.path.isfile(bin):
        return bin

    installer = os.path.join(base, "install-fzf")
    curl -L -o @(installer) https://raw.githubusercontent.com/junegunn/fzf/master/install
    bash @(installer) --bin
    os.remove(installer)
    return bin


ghq_names = {
    ("Darwin", ("64bit", "")): "ghq_darwin_amd64.zip"
}


def ghq(base):
    bin = os.path.join(base, "bin", "ghq")
    if os.path.isfile(bin):
        return bin

    import requests
    import github

    name = ghq_names[(platform.system(), platform.architecture())]
    for asset in github.latest("motemen", "ghq")["assets"]:
        if asset["name"] == name:
            break
    else:
        raise ValueError(f"no asset: {name}")

    resp = requests.get(asset["browser_download_url"])
    with zipfile.ZipFile(BytesIO(resp.content)) as z:
        path = z.extract("ghq", path=os.path.join(base, "bin"))
    os.chmod(path, 0o755)
    return path