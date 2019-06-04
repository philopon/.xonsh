def initialize_xonsh():
    $XONSH_SHOW_TRACEBACK = True
    $XONSH_INIT_BENCH = False

    import os
    import sys
    import subprocess

    XONSH_BASE_DIR = os.path.expanduser("~/.xonsh")
    sys.path.append(os.path.join(XONSH_BASE_DIR, "lib"))
    $RIPGREP_CONFIG_PATH = os.path.join(XONSH_BASE_DIR, "ripgreprc")
    $GO111MODULE = "on"

    from my_xonsh_config import utils

    with utils.bench("relax limits"):
        import resource
        utils.relax_limit(resource.RLIMIT_NPROC, 128)

    with utils.bench("pip install"):
        from my_xonsh_config import install

        install.package("prompt_toolkit")
        install.package("pygments")
        install.package("requests")
        install.package("numpy")
        install.package("matplotlib")
        install.package("tqdm")
        install.package("click")
        install.package("pillow", "PIL")
        install.pip("iterm2_tools")

    with utils.bench("bin install"):
        install.ghq(XONSH_BASE_DIR)
        install.jq(XONSH_BASE_DIR)
        install.peco(XONSH_BASE_DIR)
        install.ripgrep(XONSH_BASE_DIR)
        install.exa(XONSH_BASE_DIR)
        install.fd(XONSH_BASE_DIR)
        install.gotop(XONSH_BASE_DIR)
        dbxcli = install.dbxcli(XONSH_BASE_DIR)
        trans = install.trans(XONSH_BASE_DIR)
        it2copy = install.it2copy(XONSH_BASE_DIR)
        install.imgcat(XONSH_BASE_DIR)

    with utils.bench("global config"):
        $XONSH_HISTORY_BACKEND = 'sqlite'
        $AUTO_PUSHD = True
        $COMPLETIONS_MENU_ROWS = 20
        $DIRSTACK_SIZE = 50
        $XONSH_HISTORY_SIZE = (20 * 1024, 'commands')
        $CASE_SENSITIVE_COMPLETIONS = True
        $SUBSEQUENCE_PATH_COMPLETION = False

        $HOMEBREW_NO_ANALYTICS = 1
        $HOMEBREW_NO_AUTO_UPDATE = 1
        $COLOR_RESULTS = False

    with utils.bench("add PATH"):
        utils.add_PATH(
            os.path.join(XONSH_BASE_DIR, "cmd"),
            os.path.join(XONSH_BASE_DIR, "bin"),
            "~/miniconda3/bin",
            "~/.config/yarn/global/node_modules/.bin",
            "~/.cargo/bin",
            "/usr/local/bin",
        )

    with utils.bench("set PROMPT"):
        from my_xonsh_config.prompt import set_prompt
        set_prompt()

    with utils.bench("key binding"):
        from my_xonsh_config.keybindings import custom_keybindings
        events.on_ptk_create(custom_keybindings)

    with utils.bench("repr_pretty"):
        from my_xonsh_config import repr_pretty
        events.on_import_post_exec_module(repr_pretty.handler)

    with utils.bench("matplotlib"):
        @events.on_import_post_exec_module
        def set_matplotlib_backend(module=None, **kwargs):
            if module.__name__ == 'matplotlib':
                module.use('svg')

        xontrib load mpl

    with utils.bench("initialize variables"):
        def initialize_variables():
            globals().update([
                ("np", utils.lazymodule("numpy")),
                ("tqdm", utils.lazymodule("tqdm", "tqdm")),
                ("os", utils.lazymodule("os")),
            ])

        initialize_variables()

    with utils.bench("conda"):
        from my_xonsh_config import conda_wrapper
        aliases['conda'] = conda_wrapper.conda
        aliases['conda-activate'] = conda_wrapper.conda_activate
        __xonsh__.completers['conda'] = conda_wrapper.completer
        __xonsh__.completers.move_to_end('conda', False)

        in_conda = False
        xconda = os.path.join(os.path.dirname(sys.executable), 'conda')
        if os.path.isfile(xconda):
            aliases['xconda'] = xconda
            in_conda = True

    with utils.bench("aliases"):
        @utils.alias
        def reset(args=()):
            xonsh-reset
            initialize_variables()

        @utils.alias("pull-xonshrc")
        def pull_xonshrc(args=()):
            with utils.workdir(XONSH_BASE_DIR):
                git pull

        if 'SSH_CONNECTION' in ${...}:
            @utils.alias
            def dl(args=()):
                for f in args:
                    @(dbxcli) put @(f) / post/@(f)
        vi = utils.which("nvim") or utils.which('vim')
        if vi is not None:
            aliases["vi"] = vi
            aliases["vim"] = vi

        aliases['xpython'] = sys.executable
        aliases['xonsh'] = [sys.executable, '-m', 'xonsh']
        aliases['trans'] = [trans, '-show-translation-phonetics=n',
                            '-show-prompt-message=n', '-show-languages=n', '-show-alternatives=n']

        aliases['source-bash'] = ["source-foreign", "bash", "--sourcer=source", "--extra-args=--norc"]

        @utils.alias("update-xonsh")
        def update_xonsh(args=()):
            pull-xonshrc
            xconda update --all
            xpython - m pip_review - -interactive

        if utils.which("exa"):
            aliases["ls"] = "exa"

        if utils.which("otool"):
            aliases["ldd"] = "otool -L"

        if not utils.which("/opt/ksched/bin/kstat"):
            aliases["kstat"] = ['ssh', 'k.aics.riken.jp', '/opt/ksched/bin/kstat', '-A', '--filter', 'user=$(whoami)']

	if utils.which("code-insiders"):
	    aliases["code"] = "code-insiders"

        aliases['la'] = 'ls -a'
        aliases['ll'] = 'ls -l'
        aliases['llh'] = 'ls -lh'
        aliases["pbcopy"] = it2copy

        aliases["c"] = "pbcopy"
        aliases["p"] = "pbpaste"

        @utils.alias("pn")
        def pn(args=()):
            p = subprocess.run("pbpaste", stdout=subprocess.PIPE)
            print(" ".join(p.stdout.decode().split("\n")))

    local_config = os.path.join(XONSH_BASE_DIR, "local.xsh")
    if os.path.isfile(local_config):
        source @(local_config)


initialize_xonsh()
del initialize_xonsh
