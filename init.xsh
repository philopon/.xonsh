def initialize_xonsh():
    import os
    import sys
    from functools import partial

    XONSH_BASE_DIR = os.path.expanduser("~/.xonsh")
    sys.path.append(os.path.join(XONSH_BASE_DIR, "lib"))

    import install

    install.pip("prompt_toolkit")
    install.pip("pygments")
    install.pip("requests")
    install.pip("numpy")
    install.pip("matplotlib")
    install.pip("iterm2_tools")
    install.pip("pillow", "PIL")

    fzf_path = install.fzf(XONSH_BASE_DIR)
    ghq_path = install.ghq(XONSH_BASE_DIR)

    import conda_wrapper

    $XONSH_HISTORY_BACKEND = 'sqlite'
    $AUTO_CD = True
    $AUTO_PUSHD = True
    $COMPLETIONS_MENU_ROWS = 20
    $DIRSTACK_SIZE = 50
    $XONSH_HISTORY_SIZE = (20 * 1024, 'commands')
    $XONSH_AUTOPAIR = True
    $CASE_SENSITIVE_COMPLETIONS = True
    $SUBSEQUENCE_PATH_COMPLETION = False

    $HOMEBREW_NO_ANALYTICS = 1
    $HOMEBREW_NO_AUTO_UPDATE = 1
    $COLOR_RESULTS = False

    import utils

    utils.add_PATH(
        os.path.join(XONSH_BASE_DIR, "bin"),
        "~/miniconda3/bin",
        "/usr/local/bin",
    )

    conda_path = $(which conda)

    from prompt import set_prompt
    set_prompt()

    from keybindings import custom_keybindings
    events.on_ptk_create(partial(custom_keybindings, fzf_path=fzf_path, ghq_path=ghq_path, conda_path=conda_path))

    import repr_pretty
    events.on_import_post_exec_module(repr_pretty.handler)

    @events.on_import_post_exec_module
    def set_matplotlib_backend(module=None, **kwargs):
        if module.__name__ == 'matplotlib':
            return module.use('svg')

    def initialize_variables():
        np = utils.lazymodule("numpy")

        globals().update(locals())

    initialize_variables()

    def reset(args):
        xonsh-reset
        initialize_variables()

    aliases['reset'] = reset

    aliases['conda'] = partial(conda_wrapper.conda, conda_path=conda_path)

    xconda = os.path.join(os.path.dirname(sys.executable), 'conda')
    if os.path.isfile(xconda):
        aliases['xconda'] = xconda


initialize_xonsh()
del initialize_xonsh
