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
