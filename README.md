# kmatrix

my take on cmatrix, written in Python.

## Installation

Needs Python 3.13+ and pipx.

```bash
git clone https://github.com/DamienBlackwood/kmatrix
cd kmatrix
pipx install .
```

Then just run `kmatrix`.

**Windows:** Python 3.14+ breaks `windows-curses`, so stick to 3.13. pipx should still work, but if not:

```bash
py -3.13 -m pip install windows-curses
py -3.13 kmatrix.py
```

## Keyboard

| Key | Action |
|-----|--------|
| `+` / `-` | Speed up / down |
| `c` | Cycle color theme |
| `r` | Reverse direction |
| `?` | Show help |
| `h` | Experimental features |
| `m` | Toggle character mutation |
| `d` | Toggle sparse density |
| `x` | Toggle long trails |
| `space` | Pause |
| `q` / `esc` | Quit |

