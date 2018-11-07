import re
from io import StringIO

re_export = re.compile(r'\\?(export\s+)?(\S+)=([\'"]([^\'"]*)[\'"]|(\S+))')
re_unset = re.compile(r'\\?unset\s+(\S+)')

def eval_posix(line, ignore_envs=None):
    matched = re_export.match(line)
    if matched:
        _, key, _, qval, val = matched.groups()
        if ignore_envs and key in ignore_envs:
            return

        __xonsh__.env[key] = qval or val
        return

    matched = re_unset.match(line)
    if matched:
        key, = matched.groups()
        del __xonsh__.env[key]
        return

    raise ValueError("unknown posix line: {}".format(line.strip()))

def conda_activate(args):
    result = $(conda shell.posix activate @(args))
    for line in StringIO(result):
        eval_posix(line, {'PS1'})

def conda_deactivate(args):
    result = $(conda shell.posix deactivate)
    for line in StringIO(result):
        eval_posix(line, {'PS1'})

def conda(args):
    if args[0] == 'activate':
        return conda_activate(args[1:])
    elif args[0] == 'deactivate':
        return conda_deactivate([])

    command conda @(args)

def env_name():
    env = __xonsh__.env.get('CONDA_DEFAULT_ENV', '')
    if env:
        return "({}) ".format(env)
    else:
        return ""