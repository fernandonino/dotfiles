#!/usr/bin/env python3
"""Status bar colors for tmux, looked up per repo (or per plain directory).

Usage: dir-color.py <path> bg|fg

Keys in COLORS are repo roots, or plain directories outside a git repo.
Keys may start with "~", so one entry works on macOS and Linux.
Matching is exact after resolving symlinks.

  bg -> the mapped background color, or "default" if there is no entry
  fg -> white or black, whichever has the higher contrast with bg,
        or "default" if there is no entry
"""

import os
import sys

COLORS = {
    "~/src/panorama": "#8f0c00",
    "~/src/panorama-api": "#d33e43",
    "~/src/fern-fe": "#b8d5b8",
    "~/src/writing": "#00abe7",
    "~/src/lpulse": "#98ce00",
    "~/src/mistune-json": "#0081af",
}

WHITE = (245, 245, 245)
BLACK = (17, 17, 17)


def normalize(path):
    return os.path.realpath(os.path.expanduser(path))


def find_repo_root(path):
    """Walk up from path to the nearest directory containing .git (dir or file)."""
    current = path
    while True:
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def lookup(path):
    """Return the mapped hex color for path, or None if there is no entry."""
    mapping = {normalize(key): color for key, color in COLORS.items()}
    path = normalize(path)
    # Exact match first, so a plain directory entry still works inside a git repo
    # (for example, a home directory that is itself a repo).
    if path in mapping:
        return mapping[path]
    root = find_repo_root(path)
    if root is not None:
        return mapping.get(root)
    return None


def parse_hex(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _linear(channel):
    c = channel / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    r, g, b = (_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def foreground(bg):
    return max((WHITE, BLACK), key=lambda fg: contrast(fg, bg))


def to_hex(rgb):
    return "#%02x%02x%02x" % rgb


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[2] not in ("bg", "fg"):
        sys.exit("usage: dir-color.py <path> bg|fg")
    path, role = sys.argv[1], sys.argv[2]
    color = lookup(path)
    if color is None:
        print("default")
    elif role == "bg":
        print(color)
    else:
        print(to_hex(foreground(parse_hex(color))))
