import os
from xonsh import dirstack


def ghq(event, ghq, fzf):
    result = $(@(ghq) list | @(fzf) | cat)  # cat: avoid xonsh & fzf bug

    if result:
        path = os.path.join($(ghq root).strip(), result.strip())
        dirstack.cd([path])

    event.current_buffer.validate_and_handle()  # refresh prompt


def history(event, fzf):
    result = ![history show all | @(fzf) --tac | cat]

    if result.returncode == 0:
        choice = "".join(line for line in result).strip()
        event.cli.renderer.erase()
        event.current_buffer.insert_text(choice)
