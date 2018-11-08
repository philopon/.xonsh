def initialize_xonsh():
    import os
    import sys
    from functools import partial
    import re

    XONSH_BASE_DIR = os.path.expanduser("~/.xonsh")
    sys.path.append(os.path.join(XONSH_BASE_DIR, "lib"))

    import install

    install.pip("prompt_toolkit")
    install.pip("pygments")
    install.pip("requests")
    fzf_path = install.fzf(XONSH_BASE_DIR)
    ghq_path = install.ghq(XONSH_BASE_DIR)

    import conda_wrapper
    import fzf
    import utils

    $XONSH_HISTORY_BACKEND = 'sqlite'
    $AUTO_CD = True
    $AUTO_PUSHD = True
    $COMPLETIONS_MENU_ROWS = 20
    $DIRSTACK_SIZE = 50
    $XONSH_HISTORY_SIZE = (20 * 1024, 'commands')

    utils.add_PATH(
        os.path.join(XONSH_BASE_DIR, "bin"),
        "/usr/local/bin",
        "~/miniconda3/bin",
    )

    $PROMPT = (
        '{env_name:{}}'
        '{BOLD_GREEN}{user}{ssh_color}@{hostname} '
        '{BOLD_BLUE}{cwd}'
        '{branch_color}{curr_branch: ({})}{NO_COLOR}\n'
        '{BOLD_BLUE}{prompt_end}{NO_COLOR} '
    )

    def ssh_color():
        if 'SSH_CONNECTION' in ${...}:
            return '{INTENSE_RED}'
        else:
            return '{BOLD_GREEN}'

    $PROMPT_FIELDS['env_name'] = conda_wrapper.env_name
    $PROMPT_FIELDS['ssh_color'] = ssh_color
    aliases['conda'] = conda_wrapper.conda

    @events.on_ptk_create
    def custom_keybindings(bindings, **kwargs):
        from prompt_toolkit.keys import Keys
        from xonsh import dirstack

        bindings.add(Keys.ControlG)(partial(fzf.ghq, ghq=ghq_path, fzf=fzf_path))
        bindings.add(Keys.ControlR)(partial(fzf.history, fzf=fzf_path))

        @bindings.add(Keys.ControlT)
        def popd(event):
            dirstack.popd([])
            event.current_buffer.validate_and_handle()  # refresh prompt

        spaces = re.compile(r' +')
        @bindings.add(Keys.ControlF)
        def complete_suggestion(event):
            buf = event.current_buffer
            s = buf.suggestion
            if s:
                fs = spaces.split(s.text)
                buf.insert_text((' ' + fs[1] if fs[0] == '' else fs[0]) + " ")
            else:
                buf.cursor_right()


initialize_xonsh()
del initialize_xonsh
