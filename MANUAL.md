# CONTROLS

Inside the app, press any of the following:

`+` / `-`
:   Speed up / slow down.

`c`
:   Cycle color theme.

`r`
:   Reverse direction.

`space`
:   Pause.

`?`
:   Toggle help overlay.

`h`
:   Toggle experimental features panel.

`m`
:   Toggle character mutation.

`d`
:   Toggle sparse density.

`x`
:   Toggle long trails.

`q` / `esc`
:   Quit.

# EXAMPLES

`kmatrix`
:   Run the matrix rain.

`pipx upgrade kmatrix`
:   Upgrade to the latest version.

# FILES

`~/.kmatrix`
:   Persistent config file. Stores theme, speed, and more across sessions.

# INSTALLATION

Requires Python 3.13+.

**Recommended (pipx):**

```bash
git clone https://github.com/DamienBlackwood/kmatrix.git
cd kmatrix
pipx install .
```

Then just run `kmatrix` from anywhere.

```bash
pipx upgrade kmatrix # for any future updates 
```

Keep in mind that to be able to update, you'll need to pull the latest github version in your respective directory.

**Manual:**

```bash
python kmatrix.py
```

**Windows:**

Python 3.14+ breaks `windows-curses`. Stick to 3.13 and install the dependency first if running manually:

```bash
py -3.13 -m pip install windows-curses
py -3.13 kmatrix.py
```
