import os
from xonsh import dirstack
import subprocess

from xonsh.proc import HiddenCommandPipeline
from xonsh.built_ins import run_subproc, SubprocSpec


def ghq(event):
    result = run_subproc([['ghq', 'list'], '|', ["peco", "--layout=bottom-up"]], captured="stdout")

    if result != "":
        root = run_subproc([["ghq", 'root']], captured="stdout")
        path = os.path.join(root.strip(), result.strip())
        dirstack.cd([path])

    event.current_buffer.validate_and_handle()  # refresh prompt


def history(event):
    history = list(__xonsh__.history.all_items())
    peco = SubprocSpec.build(["peco"]).binary_loc
    cmd = subprocess.Popen([peco, "--layout=bottom-up", "--null"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    index, _ = cmd.communicate(b"\n".join(
        "{}\x00{}".format(h['inp'].split("\n")[0], i).encode()
        for i, h in enumerate(history)
    ))

    if index == b"":
        return

    choice = history[int(index)]["inp"]
    event.cli.renderer.erase()
    event.current_buffer.insert_text(choice)
