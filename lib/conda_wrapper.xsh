import sys
import os
import json

from xonsh.lazyasd import lazyobject

from utils import OneLineCache


def conda_activate(args):
    if len(args) == 1:
        conda = $(which --skip-alias conda)
        source-bash $(@(conda) shell.posix activate @(args))
        return

    if len(args) == 2:
        conda, env = args
        source-bash $(@(conda) shell.posix activate @(env))
        return

    print("Usage: conda-activate [CONDA_PATH] ENV_NAME")
    return sys.exit(1)


def conda(args):
    conda = $(which --skip-alias conda)
    if len(args) == 0:
        @(conda)
        return

    if args[0] == 'activate':
        source-bash $(@(conda) shell.posix activate @(args))
    elif args[0] == 'deactivate':
        source-bash $(@(conda) shell.posix deactivate)
    else:
        @(conda) @(args)


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
