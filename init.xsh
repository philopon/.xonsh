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
    fzf_path = install.fzf(XONSH_BASE_DIR)
    ghq_path = install.ghq(XONSH_BASE_DIR)
    conda_path = $(which conda)

    import conda_wrapper
    import utils
    from prompt import set_prompt
    from keybindings import custom_keybindings

    $XONSH_HISTORY_BACKEND = 'sqlite'
    $AUTO_CD = True
    $AUTO_PUSHD = True
    $COMPLETIONS_MENU_ROWS = 20
    $DIRSTACK_SIZE = 50
    $XONSH_HISTORY_SIZE = (20 * 1024, 'commands')
    $XONSH_AUTOPAIR = True
    $CASE_SENSITIVE_COMPLETIONS = True

    $HOMEBREW_NO_ANALYTICS = 1
    $HOMEBREW_NO_AUTO_UPDATE = 1

    utils.add_PATH(
        os.path.join(XONSH_BASE_DIR, "bin"),
        "~/miniconda3/bin",
        "/usr/local/bin",
    )

    aliases['conda'] = partial(conda_wrapper.conda, conda_path=conda_path)

    events.on_ptk_create(partial(custom_keybindings, fzf_path=fzf_path, ghq_path=ghq_path, conda_path=conda_path))

    set_prompt()


initialize_xonsh()
del initialize_xonsh
