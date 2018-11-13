import os
import json

from xonsh.lazyasd import lazyobject

from utils import OneLineCache


def conda(args, *, conda_path):
    if len(args) == 0:
        @(conda_path)
        return

    if args[0] == 'activate':
        source-bash $(@(conda_path) shell.posix activate @(args))
    elif args[0] == 'deactivate':
        source-bash $(@(conda_path) shell.posix deactivate)
    else:
        @(conda_path) @(args)


def env_name():
    env = __xonsh__.env.get('CONDA_DEFAULT_ENV', '')
    if env:
        return "({}) ".format(env)
    else:
        return ""

@lazyobject
def CONDA_COMMANDS():
    return frozenset([
        "clean", "config", "create", "help", "info",
        "install", "list", "package", "remove", "uninstall",
        "search", "update", "upgrade", "env",
        "activate", "deactivate",
        "-h", "--help",
        "v", "--version",
    ])


def get_conda_envs():
    result = $(conda env list --json)
    envs = json.loads(result)["envs"]
    return frozenset(map(os.path.basename, envs))


CONDA_ENVS = OneLineCache(get_conda_envs)


def completer(prefix, line, begidx, endidx, ctx):
    command = line.split()
    if next(iter(command), None) != "conda":
        return {}

    if len(command) == 1:
        return frozenset(CONDA_COMMANDS)

    if len(command) == 2 and line[-1:] != " ":
        return {c + " " for c in CONDA_COMMANDS if c.startswith(prefix)}

    if command[1] == "activate":
        return {e for e in CONDA_ENVS if e.startswith(prefix)}
