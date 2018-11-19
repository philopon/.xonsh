import os
from logging import getLogger, StreamHandler, INFO


logger = getLogger(__name__)
logger.setLevel(INFO)
logger.addHandler(StreamHandler())


def pip(pkg, pyname=None):
    import importlib
    if not importlib.util.find_spec(pyname or pkg):
        xpip install @(pkg)


def github_releases(bin_name, repo, **spec):
    import platform
    import requests
    from io import BytesIO
    import re

    def wrap(install):
        def installer(base):
            bin_path = os.path.join(base, "bin", bin_name)
            if os.path.isfile(bin_path):
                return bin_path

            sys_arch = f"{platform.system().lower()}_{platform.machine()}"

            pattern = spec[sys_arch]
            logger.info("installing {} ...".format(repo))

            with requests.get(f"https://api.github.com/repos/{repo}/releases/latest") as r:
                for asset in r.json()["assets"]:
                    if re.match(pattern, asset["name"]):
                        break
                else:
                    raise ValueError(f"no asset: {pattern}")

            with requests.get(asset["browser_download_url"]) as resp:
                install(BytesIO(resp.content), bin_path)
                logger.info("installing {}: done".format(repo))
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
