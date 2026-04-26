# Changelog

## v0.3.0

Render rewrite — delta drawing, fixed frame cap, smooth stepping, and persistent settings.

- Replaced chunk-based dirty region tracking with delta drawing. Only changed cells are re-drawn each frame.
- Fixed frame timing. Sleep is now `TARGET_FRAME_TIME - elapsed_work` instead of a blind `sleep(0.016)`.
- Pre-computed color attributes into `ATTR[]` to avoid repeated `color_pair()` and `A_BOLD` calls.
- Culled drop trails to the visible slice instead of iterating the full length and bounds checking every index.
- Cached overlays. Rebuild only on dimension or visibility change.
- Removed redundant `scr.move(y, x)` before `addch()`. Uses `scr.addch(y, x, ch, attr)` directly.

### Smoothness

- Added sub-pixel accumulator to drops. Slow drops no longer jitter between 0px and 1px per frame.
- Added FPS detection. Defaults to 60 FPS, switches to 120 FPS on Alacritty / Kitty / Ghostty / WezTerm / Rio. Override with `KMATRIX_FPS`.

### Overlays

- Widened overlay text boxes so rain no longer bleeds through the right edge.
- Experimental panel shows `[on]` / `[off]` labels next to toggles.
- Renamed panel header to "experimental settings".
- Added `'delay'` phase before paint-in so density rises from falling rain instead of teleporting.
- Only wakes completely off-screen drops during transitions. Prevents trails from appearing mid-screen.
- Spam guard: `h` / `?` keypresses are ignored while a transition is running.

### Added

- `MANUAL.md` for full installation, controls, and file reference.
- `py-modules` declaration to `pyproject.toml` for clean pipx installs.
- Styled bottom bar. Version left, handle right.
- `mutate`, `sparse`, and `long` settings now persist in `~/.kmatrix`.

### Fixes

- Fixed stale `bar_attr` reference when the bottom bar is hidden.

---

## v0.2.0

Renderer refactor — dirty tracking, themes, controls, config, pipx.

- Implemented dirty region tracking with per-chunk invalidation for overlay transitions.
- Six themes: green, blue, red, purple, greyscale, ocean.
- Speed control with `+` / `-`, reverse with `r`, pause with space.
- Experimental toggles: `m` for mutation, `d` for sparse density, `x` for long trails.
- Help (`?`) and experimental (`h`) overlays with transition animations.
- Persistent config saved to `~/.kmatrix` — theme, speed, reverse.
- pipx installable via `pyproject.toml` with setuptools entry point.
- Added `requirements.txt` and `windows-curses` note for Python 3.13+ on Windows.
- Added `.gitattributes` for normalized line endings.

## v0.2.1

- Added `LICENSE.md`.
- Cleaned up `README.md`.

## v0.1.0

- Initial release.
