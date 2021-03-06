import os
import sys
from logging import getLogger, StreamHandler, INFO
from functools import wraps

from xonsh.built_ins import run_subproc

logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler())


def check_bin(bin_name):
    def wrap(f):
        @wraps(f)
        def wrapped(base):
            bin_path = os.path.join(base, "bin", bin_name)
            if os.path.isfile(bin_path):
                return bin_path

            return f(bin_path)

        return wrapped

    return wrap


def get_conda():
    b = sys.prefix
    for cand in ["bin/conda", "../../bin/conda"]:
        p = os.path.join(b, cand)
        if os.path.isfile(p):
            return p


def get_conda_prefix():
    p = sys.prefix
    m = os.path.join(p, "conda-meta")
    if os.path.isdir(m) and os.listdir(m):
        return p


def package(pkg, pyname=None):
    import importlib

    if importlib.util.find_spec(pyname or pkg):
        return

    conda = get_conda()
    if conda is None:
        return pip(pkg, pyname)

    prefix = get_conda_prefix()
    run_subproc([[conda, "install", "-yp", prefix, pkg]])


def pip(pkg, pyname=None):
    import importlib

    if importlib.util.find_spec(pyname or pkg):
        return

    run_subproc([["xpip", "install", pkg]])


def arch_pair():
    import platform

    return "{}_{}".format(platform.system().lower(), platform.machine())


def github_releases(bin_name, repo, **spec):
    def wrap(install):
        @check_bin(bin_name)
        def installer(bin_path):
            import requests
            from tqdm import tqdm
            from io import BytesIO
            import re

            pattern = spec.get(arch_pair())

            if pattern is None:
                return

            logger.info("installing {} ...".format(repo))

            with requests.get(
                "https://api.github.com/repos/{}/releases".format(repo)
            ) as r:
                for asset in (asset for rel in r.json() for asset in rel["assets"]):
                    if re.match(pattern, asset["name"]):
                        break
                else:
                    raise ValueError("no asset: {}".format(pattern))

            with requests.get(asset["browser_download_url"], stream=True) as resp, tqdm(
                total=int(resp.headers["Content-Length"]), unit="B", unit_scale=True
            ) as prog:

                bio = BytesIO()
                for chunk in resp.iter_content(chunk_size=10240):
                    bio.write(chunk)
                    prog.update(len(chunk))

                bio.name = asset["name"]
                bio.seek(0)

                install(bio, bin_path)

            logger.info("installing {} done".format(repo))
            return bin_path

        return installer

    return wrap


@github_releases(
    "ghq",
    "motemen/ghq",
    darwin_x86_64=r"ghq_darwin_amd64\.zip",
    linux_x86_64=r"ghq_linux_amd64\.zip",
)
def ghq(content, bin_path):
    import zipfile
    import shutil

    with zipfile.ZipFile(content) as z:
        name = [name for name in z.namelist() if os.path.basename(name) == os.path.basename(bin_path)][0]
        shutil.copyfileobj(z.open(name), open(bin_path, "wb"))

    os.chmod(bin_path, 0o755)


@github_releases(
    "jq", "stedolan/jq", darwin_x86_64=r"jq-osx-amd64", linux_x86_64=r"jq-linux64"
)
def jq(content, bin_path):
    import shutil

    with open(bin_path, "wb") as dst:
        shutil.copyfileobj(content, dst)
    os.chmod(bin_path, 0o755)


@github_releases(
    "dbxcli",
    "dropbox/dbxcli",
    darwin_x86_64=r"dbxcli-darwin-amd64",
    linux_x86_64=r"dbxcli-linux-amd64",
    linux_armv7l=r"dbxcli-linux-arm",
)
def dbxcli(content, bin_path):
    import shutil

    with open(bin_path, "wb") as dst:
        shutil.copyfileobj(content, dst)
    os.chmod(bin_path, 0o755)


@github_releases(
    "exa",
    "ogham/exa",
    darwin_x86_64=r"exa-macos-x86_64-[0-9.]+\.zip",
    linux_x86_64=r"exa-linux-x86_64-[0-9.]+\.zip",
)
def exa(content, bin_path):
    import shutil
    import zipfile
    import platform
    import subprocess

    if (
        platform.system() == "Linux"
        and float(
            subprocess.run(["ldd", "--version"], stdout=subprocess.PIPE)
            .stdout.split(b"\n")[0]
            .split()[-1]
        )
        < 2.18
    ):
        with open(bin_path, "wb"):
            return

    with zipfile.ZipFile(content) as z:
        shutil.copyfileobj(z.open(z.namelist()[0]), open(bin_path, "wb"))

    os.chmod(bin_path, 0o755)


@github_releases(
    "peco",
    "peco/peco",
    darwin_x86_64=r"peco_darwin_amd64\.zip",
    linux_x86_64=r"peco_linux_amd64\.tar\.gz",
    linux_armv7l=r"peco_linux_arm\.tar\.gz",
)
def peco(content, bin_path):
    import shutil

    if content.name.endswith(".zip"):
        import zipfile

        with zipfile.ZipFile(content) as z:
            shutil.copyfileobj(
                z.open(
                    [
                        name
                        for name in z.namelist()
                        if os.path.basename(name) == os.path.basename(bin_path)
                    ][0]
                ),
                open(bin_path, "wb"),
            )

    if content.name.endswith(".tar.gz"):
        import tarfile

        with tarfile.open(mode="r:gz", fileobj=content) as t:
            shutil.copyfileobj(
                t.extractfile(
                    [
                        name
                        for name in t.getnames()
                        if os.path.basename(name) == os.path.basename(bin_path)
                    ][0]
                ),
                open(bin_path, "wb"),
            )

    os.chmod(bin_path, 0o755)


@github_releases(
    "rg",
    "BurntSushi/ripgrep",
    darwin_x86_64=r"ripgrep-[0-9.]+-x86_64-apple-darwin\.tar\.gz",
    linux_x86_64=r"ripgrep-[0-9.]+-x86_64-unknown-linux-musl\.tar\.gz",
    linux_armv7l=r"ripgrep-[0-9.]+-arm-unknown-linux-gnueabihf\.tar\.gz",
)
def ripgrep(content, bin_path):
    import shutil
    import tarfile

    with tarfile.open(mode="r:gz", fileobj=content) as t:
        shutil.copyfileobj(
            t.extractfile(
                [
                    name
                    for name in t.getnames()
                    if os.path.basename(name) == os.path.basename(bin_path)
                ][0]
            ),
            open(bin_path, "wb"),
        )

    os.chmod(bin_path, 0o755)


@github_releases(
    "fd",
    "sharkdp/fd",
    darwin_x86_64=r"fd-v[0-9.]+-x86_64-apple-darwin\.tar\.gz",
    linux_x86_64=r"fd-v[0-9.]+-x86_64-unknown-linux-musl\.tar\.gz",
    linux_armv7l=r"fd-v[0-9.]+-arm-unknown-linux-gnueabihf\.tar\.gz",
)
def fd(content, bin_path):
    import shutil
    import tarfile

    with tarfile.open(mode="r:gz", fileobj=content) as t:
        shutil.copyfileobj(
            t.extractfile(
                [
                    name
                    for name in t.getnames()
                    if os.path.basename(name) == os.path.basename(bin_path)
                ][0]
            ),
            open(bin_path, "wb"),
        )

    os.chmod(bin_path, 0o755)


@github_releases(
    "gotop",
    "cjbassi/gotop",
    darwin_x86_64=r"gotop_[0-9.]+_darwin_amd64.tgz",
    linux_x86_64=r"gotop_[0-9.]+_linux_amd64.tgz",
)
def gotop(content, bin_path):
    import shutil
    import tarfile

    with tarfile.open(mode="r:gz", fileobj=content) as t:
        shutil.copyfileobj(
            t.extractfile(
                [
                    name
                    for name in t.getnames()
                    if os.path.basename(name) == os.path.basename(bin_path)
                ][0]
            ),
            open(bin_path, "wb"),
        )

    os.chmod(bin_path, 0o755)


@check_bin("it2copy")
def it2copy(bin_path):
    import requests

    with requests.get(
        "https://iterm2.com/utilities/it2copy", stream=True
    ) as resp, open(bin_path, "wb") as o:
        for chunk in resp.iter_content(chunk_size=10240):
            o.write(chunk)

    os.chmod(bin_path, 0o755)
    return bin_path


@check_bin("imgcat")
def imgcat(bin_path):
    import requests

    with requests.get("https://iterm2.com/utilities/imgcat", stream=True) as resp, open(
        bin_path, "wb"
    ) as o:
        for chunk in resp.iter_content(chunk_size=10240):
            o.write(chunk)

    os.chmod(bin_path, 0o755)
    return bin_path


@check_bin("trans")
def trans(bin_path):
    import requests

    with requests.get("https://git.io/trans", stream=True) as resp, open(bin_path, "wb") as o:
        for chunk in resp.iter_content(chunk_size=10240):
            o.write(chunk)

    os.chmod(bin_path, 0o755)
    return bin_path
