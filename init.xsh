def initialize_xonsh():
    import os
    import sys
    from functools import partial

    XONSH_BASE_DIR = os.path.expanduser("~/.xonsh")
    sys.path.append(os.path.join(XONSH_BASE_DIR, "lib"))

    import install
    import conda_wrapper
    import fzf
    import utils

    install.pip("prompt_toolkit")
    install.pip("pygments")
    fzf_path = install.fzf(XONSH_BASE_DIR)

    $XONSH_HISTORY_BACKEND = 'sqlite'
    $AUTO_CD = True
    $AUTO_PUSHD = True
    $COMPLETIONS_MENU_ROWS = 20
    $DIRSTACK_SIZE = 50
    $XONSH_HISTORY_SIZE = (20 * 1024, 'commands')

    utils.add_PATH(
        "/usr/local/bin",
        "~/miniconda3/bin",
    )

    $PROMPT = (
        '{env_name:{}}'
        '{BOLD_GREEN}{user}@{hostname} '
        '{BOLD_BLUE}{cwd}'
        '{branch_color}{curr_branch: ({})}{NO_COLOR}\n'
        '{BOLD_BLUE}{prompt_end}{NO_COLOR} '
    )

    $PROMPT_FIELDS['env_name'] = conda_wrapper.env_name
    aliases['conda'] = conda_wrapper.conda

    @events.on_ptk_create
    def custom_keybindings(bindings, **kwargs):
        from prompt_toolkit.keys import Keys
        from xonsh import dirstack

        bindings.add(Keys.ControlG)(partial(fzf.ghq, fzf=fzf_path))
        bindings.add(Keys.ControlR)(partial(fzf.history, fzf=fzf_path))

        @bindings.add(Keys.ControlT)
        def popd(event):
            dirstack.popd([])
            event.current_buffer.validate_and_handle()  # refresh prompt

initialize_xonsh()
del initialize_xonsh