# kmatrix

my take on cmatrix!! (but python)

## Setup

**Requires Python 3.13** (Python 3.14+ not yet supported by `windows-curses`)

```bash
# Windows
py -3.13 -m pip install -r requirements.txt
py -3.13 kmatrix.py

# Linux/macOS
pip install -r requirements.txt
python3 kmatrix.py
```

## Controls

| Key | Action |
|-----|--------|
| **C** | Cycle themes |
| **+/-** | Speed up/down |
| **SPACE** | Pause/resume |
| **R** | Reverse direction |
| **Q/ESC** | Quit |

## Features

- 60 FPS with differential rendering
- 6 color themes
