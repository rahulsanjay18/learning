#!/usr/bin/env python3
"""Turn a Vim keystroke recording (vim -W keys.log file) into the notation scripts/vimcheck.py reads.

    vim -W ~/keys.log drill.txt        # do the drill, finish with :wq
    python3 scripts/vimkeys.py ~/keys.log
    -> A;<Esc>j.j.:wq<CR>

Esc, Enter, Tab and Backspace become <Esc> <CR> <Tab> <BS>; other control keys become <C-x>; a literal '<' becomes <lt>.
Special keys Vim records as 0x80 sequences (arrows, function keys) become <special>: drills are meant to be done without them.
"""
import sys

NAMES = {"\x1b": "<Esc>", "\r": "<CR>", "\n": "<CR>", "\t": "<Tab>", "\x08": "<BS>", "\x7f": "<BS>", "<": "<lt>"}


def convert(data):
    out, i = [], 0
    while i < len(data):
        b = data[i]
        if b == 0x80:  # Vim's internal special-key code: 0x80, two bytes
            out.append("<BS>" if data[i + 1:i + 3] == b"kb" else "<special>")
            i += 3
            continue
        c = chr(b)
        out.append(NAMES.get(c) or (f"<C-{chr(b + 96)}>" if b < 32 else c))
        i += 1
    return "".join(out)


if __name__ == "__main__":
    print(convert(open(sys.argv[1], "rb").read()))
