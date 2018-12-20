#!/usr/bin/env python

import sys


def color(r, g, b, s):
    return "\x1b[48;2;{};{};{}m{}\x1b[0m".format(r, g, b, s)


def main(col):
    if len(col) == 4 and col[0] == '#':
        r, g, b = int(col[1], 16) * 17, int(col[2], 16) * 17, int(col[3], 16) * 17

    elif len(col) == 7 and col[0] == '#':
        r, g, b = int(col[1:3], 16), int(col[3:5], 16), int(col[5:7], 16)

    else:
        v = int(col)
        r, g, b = v >> 16 & 0xff, v >> 16 & 0xff, v & 0xff

    print(r, g, b)

    spaces = " " * 80
    for _ in range(5):
        print(color(r, g, b, spaces))


if __name__ == "__main__":
    main(sys.argv[1])
