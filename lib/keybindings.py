from prompt_toolkit.keys import Keys
from prompt_toolkit import filters
from prompt_toolkit.application.current import get_app
from xonsh import dirstack
from functools import partial
import fzf
import re
from common_prefix import common_prefix

def custom_keybindings(bindings, fzf_path, ghq_path, **kwargs):
    @filters.Condition
    def can_partial_complete():
        buf = get_app().current_buffer
        s = buf.suggestion
        return s and ' ' in s.text

    bindings.add(Keys.ControlG)(partial(fzf.ghq, ghq=ghq_path, fzf=fzf_path))
    bindings.add(Keys.ControlR)(partial(fzf.history, fzf=fzf_path))

    @bindings.add(Keys.ControlT)
    def popd(event):
        dirstack.popd([])
        event.current_buffer.insert_text("dirs")
        event.current_buffer.validate_and_handle()

    spaces = re.compile(r' +')

    @bindings.add(Keys.ControlF, filter=can_partial_complete)
    def partial_complete(event):
        buf = event.current_buffer
        s = spaces.split(buf.suggestion.text)
        buf.insert_text((' ' + s[1] if s[0] == '' else s[0]) + " ")

    @bindings.add(Keys.ControlP, filter=filters.has_completions)
    def history_forward(event):
        event.current_buffer.cancel_completion()
        event.current_buffer.history_backward()

    @bindings.add(Keys.ControlN, filter=filters.has_completions)
    def history_forward(event):
        event.current_buffer.cancel_completion()
        event.current_buffer.history_forward()

    @bindings.add('/', filter=filters.has_completions)
    def apply_on_slash(event):
        buf = event.current_buffer
        comp = buf.complete_state.current_completion

        if comp is not None and len(comp.text) > 1 and comp.text[-1] == '/':
            buf.apply_completion(comp)
        else:
            buf.insert_text('/')

    @bindings.add(Keys.Tab)
    def complete_common_on_tab(event):
        buf = event.current_buffer
        buf.start_completion()
        comp = buf.complete_state.completions
        if len(comp) == 0:
            return

        common = common_prefix(c.text for c in comp)
        comp_len = -comp[0].start_position
        if common and len(common) > comp_len:
            buf.delete_before_cursor(comp_len)
            buf.insert_text(common)
        else:
            buf.complete_next()
