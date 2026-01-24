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
| **C** | Cycle themes (green, blue, red, purple, grayscale, ocean) |
| **+/-** | Speed up/down |
| **SPACE** | Pause/resume |
| **R** | Reverse direction |
| **D/A** | Increase/decrease rainfall density (not fully implemented yet.) |
| **Q/ESC** | Quit |

## Features

- 60 FPS with differential rendering
- 6 color themes
- Real-time controls
