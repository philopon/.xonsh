def initialize_xonsh():
    $XONSH_SHOW_TRACEBACK = True

    import os
    import sys

    XONSH_BASE_DIR = os.path.expanduser("~/.xonsh")
    sys.path.append(os.path.join(XONSH_BASE_DIR, "lib"))

    from my_xonsh_config import install

    install.pip("prompt_toolkit")
    install.pip("pygments")
    install.pip("requests")
    install.pip("numpy")
    install.pip("matplotlib")
    install.pip("iterm2_tools")
    install.pip("tqdm")
    install.pip("pillow", "PIL")

    install.ghq(XONSH_BASE_DIR)
    install.jq(XONSH_BASE_DIR)
    install.peco(XONSH_BASE_DIR)
    install.ripgrep(XONSH_BASE_DIR)
    it2copy = install.it2copy(XONSH_BASE_DIR)

    from my_xonsh_config import conda_wrapper

    $XONSH_HISTORY_BACKEND = 'sqlite'
    $AUTO_CD = True
    $AUTO_PUSHD = True
    $COMPLETIONS_MENU_ROWS = 20
    $DIRSTACK_SIZE = 50
    $XONSH_HISTORY_SIZE = (20 * 1024, 'commands')
    $CASE_SENSITIVE_COMPLETIONS = True
    $SUBSEQUENCE_PATH_COMPLETION = False

    $HOMEBREW_NO_ANALYTICS = 1
    $HOMEBREW_NO_AUTO_UPDATE = 1
    $COLOR_RESULTS = False

    from my_xonsh_config import utils

    utils.add_PATH(
        os.path.join(XONSH_BASE_DIR, "bin"),
        "~/miniconda3/bin",
        "~/.config/yarn/global/node_modules/.bin",
        "~/.cargo/bin",
        "/usr/local/bin",
    )

    from my_xonsh_config.prompt import set_prompt
    set_prompt()

    from my_xonsh_config.keybindings import custom_keybindings
    events.on_ptk_create(custom_keybindings)

    from my_xonsh_config import repr_pretty
    events.on_import_post_exec_module(repr_pretty.handler)

    @events.on_import_post_exec_module
    def set_matplotlib_backend(module=None, **kwargs):
        if module.__name__ == 'matplotlib':
            return module.use('svg')

    def initialize_variables():
        globals().update([
            ("np", utils.lazymodule("numpy")),
            ("tqdm", utils.lazymodule("tqdm", "tqdm")),
            ("os", utils.lazymodule("os")),
        ])

    initialize_variables()

    def local_command(name, base=os.path.join(XONSH_BASE_DIR, "cmd"), exec=sys.executable):
        return [exec, os.path.join(base, name)]

    def reset(args):
        xonsh-reset
        initialize_variables()

    def pull_xonshrc(args):
        with utils.workdir(XONSH_BASE_DIR):
            git pull

    aliases['reset'] = reset
    aliases['pull-xonshrc'] = pull_xonshrc
    aliases['touchnb'] = local_command("touchnb.py")
    aliases['color'] = local_command("color.py")

    aliases['source-bash'] = ["source-foreign", "bash", "--sourcer=source", "--extra-args=--norc"]
    aliases['conda'] = conda_wrapper.conda
    aliases['conda-activate'] = conda_wrapper.conda_activate
    __xonsh__.completers['conda'] = conda_wrapper.completer
    __xonsh__.completers.move_to_end('conda', False)

    xconda = os.path.join(os.path.dirname(sys.executable), 'conda')
    if os.path.isfile(xconda):
        aliases['xconda'] = xconda

    aliases['la'] = 'ls -a'
    aliases['ll'] = 'ls -l'
    aliases['llh'] = 'ls -lh'
    aliases["pbcopy"] = it2copy


initialize_xonsh()
del initialize_xonsh
