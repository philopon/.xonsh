import os

def pip(pkg, pyname=None):
    import importlib
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


def ghq(base):
    bin = os.path.join(base, "bin", "ghq")
    if os.path.isfile(bin):
        return bin

    import platform
    import zipfile
    import requests
    import github
    from io import BytesIO

    ghq_names = {
        ("Darwin", ("64bit", "")): "ghq_darwin_amd64.zip",
        ('Linux', ('64bit', '')): "ghq_linux_amd64.zip"
    }

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
