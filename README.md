# kmatrix

Terminal Matrix rain effect in Python.

## Installation

Requires Python 3.13+ (3.14+ not supported by `windows-curses` yet).

```bash
# Windows
py -3.13 -m pip install -r requirements.txt
py -3.13 kmatrix.py

# macOS / Linux
pip install -r requirements.txt
python3 kmatrix.py
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

## Features

- Dirty region tracking for efficient rendering
- 6 color themes
- Smooth directional reversals
- Character mutation and density modes
