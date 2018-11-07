import requests


def latest(owner, repo):
    with requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases/latest") as r:
        return r.json()