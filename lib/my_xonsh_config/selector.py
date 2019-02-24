import os
from xonsh import dirstack
import subprocess

from xonsh.proc import HiddenCommandPipeline
from xonsh.built_ins import run_subproc, SubprocSpec

from . import utils


def select(cands, options=None):
    if options is None:
        options = []
    peco = utils.which("peco")
    cmd = subprocess.Popen([peco] + options, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return cmd.communicate(b"\n".join(cands))


def ghq(event):
    cands = run_subproc([['ghq', 'list']], captured='stdout').strip().split('\n')
    result, _ = select(map(lambda s: s.encode(), reversed(cands)), options=["--layout=bottom-up"])

    if len(result) > 0:
        root = run_subproc([["ghq", 'root']], captured="stdout")
        path = os.path.join(root.strip(), result.decode().strip())
        dirstack.cd([path])

    event.current_buffer.validate_and_handle()  # refresh prompt


def history(event):
    history = list(reversed(list(__xonsh__.history.all_items())))
    index, _ = select(
        ("{}\x00{}".format(h['inp'].split('\n')[0], i).encode() for i, h in enumerate(history)),
        options=["--layout=bottom-up", '--null']
    )

    if len(index) == 0:
        return

    choice = history[int(index)]["inp"]
    event.current_buffer.insert_text(choice)


def ssh(event, known_hosts='{}/.ssh/known_hosts'.format(__xonsh__.env["HOME"])):
    hosts = [
        h.split(',')[0].encode()
        for h in (h.split(' ')[0] for h in open(known_hosts))
        if ',' in h
    ]

    r, _ = select(hosts, options=["--layout=bottom-up"])
    if len(r) == 0:
        return

    event.current_buffer.insert_text("ssh {}".format(r.decode()))
    event.current_buffer.validate_and_handle()
