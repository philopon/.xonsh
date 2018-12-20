import os
from logging import getLogger, StreamHandler, INFO

from xonsh.built_ins import run_subproc

logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler())


def pip(pkg, pyname=None):
    import importlib
    if not importlib.util.find_spec(pyname or pkg):
        run_subproc([["xpip", "install", pkg]])


def github_releases(bin_name, repo, **spec):
    def wrap(install):
        def installer(base):
            import platform
            import requests
            from tqdm import tqdm
            from io import BytesIO
            import re

            bin_path = os.path.join(base, "bin", bin_name)
            if os.path.isfile(bin_path):
                return bin_path

            sys_arch = f"{platform.system().lower()}_{platform.machine()}"

            pattern = spec[sys_arch]
            logger.info("installing {} ...".format(repo))

            with requests.get(f"https://api.github.com/repos/{repo}/releases") as r:
                for asset in (asset for rel in r.json() for asset in rel["assets"]):
                    if re.match(pattern, asset["name"]):
                        break
                else:
                    raise ValueError(f"no asset: {pattern}")

            with requests.get(asset["browser_download_url"], stream=True) as resp, tqdm(total=int(resp.headers["Content-Length"]), unit="B", unit_scale=True) as prog:

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
    "ghq", "motemen/ghq",
    darwin_x86_64=r"ghq_darwin_amd64\.zip",
    linux_x86_64=r"ghq_linux_amd64\.zip",
)
def ghq(content, bin_path):
    import zipfile
    with zipfile.ZipFile(content) as z:
        path = z.extract(os.path.basename(bin_path), path=os.path.dirname(bin_path))
    os.chmod(path, 0o755)


@github_releases(
    "fzf", "junegunn/fzf-bin",
    darwin_x86_64=r"fzf-.+-darwin_amd64\.tgz",
    linux_x86_64=r"fzf-.+-linux_amd64\.tgz",
)
def fzf(content, bin_path):
    import tarfile
    with tarfile.open(mode="r:gz", fileobj=content) as t:
        t.extract(os.path.basename(bin_path), path=os.path.dirname(bin_path))
    os.chmod(bin_path, 0o755)


@github_releases("jq", "stedolan/jq",
    darwin_x86_64=r"jq-osx-amd64",
    linux_x86_64=r"jq-linux64",
)
def jq(content, bin_path):
    import shutil
    with open(bin_path, "wb") as dst:
        shutil.copyfileobj(content, dst)
    os.chmod(bin_path, 0o755)


@github_releases("peco", "peco/peco",
    darwin_x86_64=r"peco_darwin_amd64\.zip",
    linux_x86_64=r"peco_linux_amd64\.tar\.gz",
)
def peco(content, bin_path):
    import shutil
    if content.name.endswith(".zip"):
        import zipfile
        with zipfile.ZipFile(content) as z:
            shutil.copyfileobj(
                z.open([name for name in z.namelist() if os.path.basename(name) == os.path.basename(bin_path)][0]),
                open(bin_path, "wb"),
            )

    if content.name.endswith(".tar.gz"):
        import tarfile
        with tarfile.open(mode="r:gz", fileobj=content) as t:
            shutil.copyfileobj(
                t.extractfile([name for name in t.getnames() if os.path.basename(name) == os.path.basename(bin_path)][0]),
                open(bin_path, "wb")
            )

    os.chmod(bin_path, 0o755)


@github_releases("rg", "BurntSushi/ripgrep",
    darwin_x86_64=r"ripgrep-[0-9.]+-x86_64-apple-darwin\.tar\.gz",
    linux_x86_64=r"ripgrep-[0-9.]+-x86_64-unknown-linux-musl\.tar\.gz",
)
def ripgrep(content, bin_path):
    import shutil
    import tarfile
    with tarfile.open(mode="r:gz", fileobj=content) as t:
            shutil.copyfileobj(
                t.extractfile([name for name in t.getnames() if os.path.basename(name) == os.path.basename(bin_path)][0]),
                open(bin_path, "wb")
            )

    os.chmod(bin_path, 0o755)


def it2copy(base):
    import requests

    bin_path = os.path.join(base, "bin", "it2copy")
    if os.path.isfile(bin_path):
        return bin_path

    with requests.get(f"https://iterm2.com/utilities/it2copy", stream=True) as resp, open(bin_path, "wb") as o:
        for chunk in resp.iter_content(chunk_size=10240):
            o.write(chunk)

    os.chmod(bin_path, 0o755)
    return bin_path
