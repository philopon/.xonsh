import os
import re

from my_xonsh_config.utils import lazymodule
from prompt_toolkit import filters

from xonsh import dirstack
from xonsh.aliases import xonsh_exit

from . import selector
from . import conda_wrapper
from .utils import common_prefix


def custom_keybindings(bindings, **kwargs):
    get_app = lazymodule("prompt_toolkit.application.current", "get_app")

    @filters.Condition
    def in_conda_env():
        return "CONDA_DEFAULT_ENV" in __xonsh__.env

    @filters.Condition
    def no_input():
        return get_app().current_buffer.text == ""

    bindings.add("c-g", filter=no_input)(selector.ghq)
    bindings.add("c-r", filter=no_input)(selector.history)
    bindings.add("c-s", filter=no_input)(selector.ssh)

    @bindings.add("c-u", filter=no_input)
    def go_up(event):
        dirstack.cd([os.path.dirname(__xonsh__.env['PWD'])])
        event.current_buffer.validate_and_handle()

    re_partial_complete = re.compile(r'(.+?)([ /:]|$)+')

    @bindings.add("c-d", filter=no_input & ~in_conda_env)
    def ignore_eof(event):
        event.app.output.bell()

    @bindings.add("c-d", "c-d", filter=no_input & ~in_conda_env)
    def two_control_d_to_exit(event):
        event.cli.current_buffer.validate_and_handle()
        xonsh_exit([])

    @bindings.add("c-d", filter=no_input & in_conda_env)
    def conda_deactivate(event):
        conda_wrapper.deactivate()
        event.current_buffer.validate_and_handle()
