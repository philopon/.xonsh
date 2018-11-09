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

    fzf_path = install.fzf(XONSH_BASE_DIR)
    ghq_path = install.ghq(XONSH_BASE_DIR)

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
    $SUBSEQUENCE_PATH_COMPLETION = False

    $HOMEBREW_NO_ANALYTICS = 1
    $HOMEBREW_NO_AUTO_UPDATE = 1
    $COLOR_RESULTS = False

    utils.add_PATH(
        os.path.join(XONSH_BASE_DIR, "bin"),
        "~/miniconda3/bin",
        "/usr/local/bin",
    )

    conda_path = __xonsh__.commands_cache.locate_binary('conda')

    events.on_ptk_create(partial(custom_keybindings, fzf_path=fzf_path, ghq_path=ghq_path, conda_path=conda_path))
    @events.on_import_post_exec_module
    def _(module=None, **kwargs):
        if module.__name__ == 'matplotlib':
            return module.use('svg')

        if module.__name__ == 'rdkit.Chem':
            from rdkit.Chem import Draw
            from io import BytesIO
            from iterm2_tools.images import display_image_bytes

            def _mol_repr_pretty_(self, p, cycle):
                b = BytesIO()
                img = Draw.MolToImage(self)
                img.save(b, format='png')
                p.text(display_image_bytes(b.getbuffer()))

            module.Mol._repr_pretty_ = _mol_repr_pretty_

    set_prompt()

    def initialize_variables():
        import numpy as np
        globals().update(locals())

    initialize_variables()

    def reset(args):
        xonsh-reset
        initialize_variables()

    aliases['reset'] = reset

    # aliases['conda'] = partial(conda_wrapper.conda, conda_path=conda_path)

    xconda = os.path.join(os.path.dirname(sys.executable), 'conda')
    if os.path.isfile(xconda):
        aliases['xconda'] = xconda


initialize_xonsh()
del initialize_xonsh
