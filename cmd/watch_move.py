import os
import sys
import time
import shutil
import subprocess
from pathlib import Path
from logging import getLogger, StreamHandler, NullHandler
from itertools import count

import click

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer



logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Handler(FileSystemEventHandler):
    def __init__(self, src, dst):
        super().__init__()
        self.src = src
        self.dst = dst

    def on_created(self, event):
        name = os.path.relpath(event.src_path, self.src)
        i = name.find(".")
        base, ext = (name[:i], name[i:]) if i > 0 else (name, "")

        try:
            for i in count(0):
                suffix = "" if i == 0 else f"_{i}"
                dst = os.path.join(self.dst, base + suffix + ext)
                os.stat(dst)
        except FileNotFoundError:
            pass

        shutil.move(event.src_path, dst)
        logger.info(f"move {event.src_path} to {dst}")


def watcher(src, dst):
    logger.setLevel(20)
    logger.addHandler(StreamHandler())
    handler = Handler(src, dst)
    observer = Observer()
    observer.schedule(handler, src, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


@click.group()
def cli():
    pass

@cli.command()
@click.argument("SRC", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.argument("DST", type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
def register(src, dst):
    plist = Path("~/Library/LaunchAgents/watch_dropbox_and_move.plist").expanduser()
    with open(plist, "w") as p:
        p.write(f"""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>watch_dropbox_and_move</string>
	<key>ProgramArguments</key>
	<array>
		<string>{sys.executable}</string>
        <string>{sys.argv[0]}</string>
        <string>daemon</string>
        <string>{src}</string>
        <string>{dst}</string>
	</array>
    <key>EnvironmentVariables</key>
    <dict>
           <key>LC_ALL</key>
           <string>en_US.UTF-8</string>
    </dict>
	<key>KeepAlive</key>
	<true/>
	<key>RunAtLoad</key>
	<true/>
</dict>
</plist>"""[1:])
    subprocess.run(["launchctl", "unload", plist], check=True)
    subprocess.run(["launchctl", "load", plist], check=True)


@cli.command()
@click.argument("SRC", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True))
@click.argument("DST", type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True))
def daemon(src, dst):
    watcher(src, dst)


if __name__ == "__main__":
    cli()
