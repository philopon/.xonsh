import sys
import re

ansi_escape = re.compile(r'\x1B\[[0-9;]*[a-zA-Z]')

def plain(src, dst):
    for line in src:
        dst.write(ansi_escape.sub("", line))


if __name__ == "__main__":
    plain(sys.stdin, sys.stdout)
