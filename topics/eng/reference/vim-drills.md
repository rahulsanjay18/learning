# How to do (and send) a Vim drill

Each Engineering lesson opens with a 2-minute drill: turn a start text into a target text in Vim with as few keystrokes as you can.
I check it by replaying your keys in real Vim (`scripts/vimcheck.py`), so you have to send me exactly what you typed.

## Option A: record it (recommended, nothing to remember)
1. Save the start text from the lesson to a file, e.g. `drill.txt`.
2. Open it with Vim's keystroke recorder on:
   ```bash
   vim -W keys.log drill.txt
   ```
   `-W keys.log` writes every key you type to `keys.log` (overwriting it each time). Do the edit, then quit with `:wq` or `ZZ`.
3. Show the recording with the invisible keys made visible:
   ```bash
   cat -v keys.log
   ```
   Escape shows as `^[` and Enter as `^M`, e.g. `A;^[j.j.:wq^M`.
4. Paste that line into the lesson's drill box (or to me in chat). I run it with `vimcheck.py --caret`, which reads that notation
   and leaves your final `:wq` / `ZZ` out of the count.

Every key counts, including mistakes and `u` undos: that's the honest count, and it's how VimGolf scores too.

## Option B: type the keys out
Write them in Vim's own key notation: `<Esc>`, `<CR>` (Enter), `<Tab>`, `<BS>`, `<C-r>` (Ctrl+R), `<lt>` for a literal `<`.
Example for the first drill: `A;<Esc>j.j.`

## Sources
- Vim's documentation, `:help -w` and `:help -W` (starting.txt): `-w {scriptout}` records "all the characters that you type"; `-W` is
  the same but overwrites the file instead of appending. <https://vimhelp.org/starting.txt.html#-W>
- `cat -v` shows non-printing characters in `^` notation (GNU coreutils manual). <https://www.gnu.org/software/coreutils/manual/html_node/cat-invocation.html>
