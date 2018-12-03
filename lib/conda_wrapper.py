import sys
import os
import json

from xonsh.lazyasd import lazyobject

from utils import OneLineCache

from xonsh.built_ins import run_subproc


def conda_activate(args):
    if len(args) == 1:
        return activate(args[0])

    if len(args) == 2:
        conda, env = args
        return activate(env, conda)

    else:
        print("Usage: conda-activate [CONDA_PATH] ENV_NAME")
        sys.exit(1)


def which_conda():
    return run_subproc([["which", "--skip-alias", "conda"]], captured="stdout")


def activate(env, conda=None):
    if conda is None:
        conda = which_conda()

    bash = run_subproc([[conda, 'shell.posix', 'activate', env]], captured="stdout")
    run_subproc([["source-bash", bash]])


def deactivate(conda=None):
    if conda is None:
        conda = which_conda()

    bash = run_subproc([[conda, 'shell.posix', 'deactivate']], captured="stdout")
    run_subproc([["source-bash", bash]])


def conda(args):
    conda = which_conda()
    if len(args) == 0:
        run_subproc([[conda]])
        return

    if args[0] == 'activate':
        activate(args[1], conda)
    elif args[0] == 'deactivate':
        deactivate(conda)
    else:
        run_subproc([[conda] + args])


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
    conda = run_subproc([["which", "--skip-alias", "conda"]], captured="stdout")
    result = run_subproc([[conda, 'env', 'list', '--json']], captured="stdout")
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
