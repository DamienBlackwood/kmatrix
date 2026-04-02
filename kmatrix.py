#!/usr/bin/env python3
import curses, random, time

CHARS = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789"

AUTHOR  = "github.com/DamienBlackwood"
VERSION = "v0.2"

class Drop:
    def __init__(self, x, h, long=False):
        self.x = x
        self.len = random.randint(30, 60) if long else random.randint(5, 20)
        self.spd = random.uniform(0.3, 1.5)
        self.y = float(random.randint(-h, -1))
        self.chars = [random.choice(CHARS) for _ in range(self.len)]
        self.dir = 1.0
        self.target_dir = 1.0
        self.flip_delay = 0
        self.mutate_timer = random.randint(15, 40)
        self.active = True
        self.born_gen = -1

    def set_target(self, target):
        self.target_dir = target
        self.flip_delay = random.randint(0, 25)

    def update(self, h, speed=1.0, mutate=False):
        if self.flip_delay > 0:
            self.flip_delay -= 1
        else:
            self.dir += (self.target_dir - self.dir) * 0.08

        self.y += self.spd * speed * self.dir

        mutated = False
        if mutate:
            self.mutate_timer -= 1
            if self.mutate_timer <= 0:
                for _ in range(3):
                    self.chars[random.randint(0, self.len - 1)] = random.choice(CHARS)
                self.mutate_timer = random.randint(8, 20)
                mutated = True

        going_up = self.target_dir < 0
        if (going_up and self.y + self.len < 0) or (not going_up and self.y - self.len > h):
            self.y = float(random.randint(h+1, h+20)) if going_up else float(random.randint(-20, -1))
            self.spd = random.uniform(0.5, 1.8)
            self.chars = [random.choice(CHARS) for _ in range(self.len)]
            return mutated, True
        return mutated, False


def make_drops(w, h):
    return [Drop(x, h) for x in range(w)]


def main(scr):
    curses.curs_set(0); scr.nodelay(1); scr.timeout(0)
    THEMES = [
        [232,22,28,34,46,40],           # green
        [17,18,19,20,21,27],            # blue
        [52,88,124,160,196,202],        # red
        [53,89,125,161,197,171],        # purple
        [235,238,241,245,249,255],      # sleek grayscale
        [54,91,128,165,201,219]         # ocean gradient
    ]

    theme, speed = 0, 1.0

    if curses.has_colors():
        curses.start_color(); curses.use_default_colors()
        for i, c in enumerate(THEMES[theme], 1): curses.init_pair(i, c, -1)

    h, w = scr.getmaxyx()
    CHUNK = max(4, min(12, h // 20))

    paused, reverse = False, False
    show_help, show_exp = False, False
    mutate, density_sparse, long_mode = False, False, False

    phase = None
    direction = None
    snap = {}
    revealed = set()
    closing = None
    opening = None
    transition_gen = 0

    drops = make_drops(w, h)
    buf = {}
    dirty = {((y//CHUNK)*CHUNK, (x//CHUNK)*CHUNK) for y in range(h) for x in range(w)}

    HELP = [
        ("", ""),
        ("  k m a t r i x", ""),
        ("", ""),
        ("  +  /  -", "speed up / slow down"),
        ("  c",        "cycle theme"),
        ("  r",        "reverse direction"),
        ("  space",    "pause"),
        ("  h",        "experimental"),
        ("  ?",        "toggle this"),
        ("  q  /  esc","quit"),
        ("", ""),
    ]

    EXP_HELP = [
        ("", ""),
        ("  experimental", ""),
        ("", ""),
        ("  m",   "character mutation"),
        ("  d",   "sparse density"),
        ("  x",   "long trails"),
        ("", ""),
        ("  h",   "toggle this panel"),
        ("", ""),
    ]

    def build_overlay(show_h, show_e):
        pw = 32
        cells = {}
        for rows in ([HELP] if show_h else []) + ([EXP_HELP] if show_e else []):
            py = max(1, h//2 - len(rows)//2)
            px = max(1, w//2 - pw//2)
            for i, (key, desc) in enumerate(rows):
                y_ = py + i
                if y_ >= h - 1: break
                line = f"  {key:<12}{desc}".ljust(pw)
                for j, ch_ in enumerate(line):
                    if px+j < w-1:
                        attr = curses.color_pair(5)|curses.A_BOLD if i == 1 else curses.color_pair(4) if key.strip() else curses.color_pair(2)
                        cells[(y_, px+j)] = (ch_, attr)
        return cells

    def start_transition(dir_, show_h, show_e, open_which=None, close_which=None):
        nonlocal phase, direction, snap, revealed, closing, opening, transition_gen
        transition_gen += 1
        phase = 'waiting'
        direction = dir_
        sh = show_h or (open_which == 'help')
        se = show_e or (open_which == 'exp')
        snap = build_overlay(sh, se)
        revealed = set()
        closing = close_which
        opening = open_which
        for d in drops:
            d.active = True
            d.born_gen = transition_gen - 1

    while True:
        nh, nw = scr.getmaxyx()
        if nh != h or nw != w:
            h, w = nh, nw
            drops = make_drops(w, h)
            buf = {}
            CHUNK = max(4, min(12, h // 20))
            dirty = {((y//CHUNK)*CHUNK, (x//CHUNK)*CHUNK) for y in range(h) for x in range(w)}
            phase = None; direction = None; snap = {}; revealed = set(); closing = None; opening = None
            scr.clear()

        ch = scr.getch()
        if ch in (ord('q'), ord('Q'), 27): break
        if ch in (ord('+'), ord('=')): speed = min(3.0, speed + 0.2)
        if ch in (ord('-'), ord('_')): speed = max(0.2, speed - 0.2)
        if ch in (ord('c'), ord('C')):
            theme = (theme + 1) % len(THEMES)
            for i, c in enumerate(THEMES[theme], 1): curses.init_pair(i, c, -1)
        if ch in (ord(' '),): paused = not paused
        if ch in (ord('r'), ord('R')):
            reverse = not reverse
            for d in drops: d.set_target(-1.0 if reverse else 1.0)
        if phase is None:
            if ch in (ord('?'),):
                if not show_help: start_transition('in', show_help, show_exp, open_which='help')
                else: start_transition('out', show_help, show_exp, close_which='help')
            if ch in (ord('h'), ord('H')):
                if not show_exp: start_transition('in', show_help, show_exp, open_which='exp')
                else: start_transition('out', show_help, show_exp, close_which='exp')
        if ch in (ord('m'), ord('M')): mutate = not mutate
        if ch in (ord('d'), ord('D')): density_sparse = not density_sparse
        if ch in (ord('x'), ord('X')): long_mode = not long_mode
        if ch == curses.KEY_RESIZE: continue

        if paused: time.sleep(0.016); continue

        in_transition = phase is not None
        use_long = long_mode or in_transition
        use_dense = not density_sparse or in_transition

        frame = {}
        for d in drops:
            mutated, expired = d.update(h, speed, mutate)
            if expired:
                d.len = random.randint(30, 60) if use_long else random.randint(5, 20)
                d.spd = random.uniform(0.5, 1.8)
                d.y = float(random.randint(-20, -1)) if d.target_dir >= 0 else float(random.randint(h+1, h+20))
                d.chars = [random.choice(CHARS) for _ in range(d.len)]
                d.born_gen = transition_gen
                if not in_transition:
                    d.active = not density_sparse or random.random() < 0.35
            if not d.active: continue
            for i in range(d.len):
                y = int(d.y - i * (1 if d.dir >= 0 else -1))
                if 0 <= y < h-1 and 0 <= d.x < w-1:
                    col = 6 if i == 0 else 5 if i < 3 else 4 if i < 6 else 3 if i < d.len * 0.6 else 2
                    frame[(y, d.x)] = (d.chars[i], col)
                    if mutated:
                        dirty.add(((y//CHUNK)*CHUNK, (d.x//CHUNK)*CHUNK))
                    if phase in ('waiting', 'painting_in', 'painting_out') and i == 0 and d.born_gen == transition_gen and (y, d.x) in snap:
                        if (y, d.x) not in revealed:
                            revealed.add((y, d.x))
                            dirty.add(((y//CHUNK)*CHUNK, (d.x//CHUNK)*CHUNK))
                        if phase == 'waiting':
                            phase = 'painting_in' if direction == 'in' else 'painting_out'

        if phase in ('painting_in', 'painting_out') and snap and revealed >= set(snap.keys()):
            if opening == 'help': show_help = True
            if opening == 'exp':  show_exp  = True
            if closing == 'help': show_help = False
            if closing == 'exp':  show_exp  = False
            phase = None; direction = None; snap = {}; revealed = set(); closing = None; opening = None

        overlay = build_overlay(show_help, show_exp)

        for p in frame:
            if buf.get(p) != frame[p]: dirty.add(((p[0]//CHUNK)*CHUNK, (p[1]//CHUNK)*CHUNK))
        for p in buf:
            if p not in frame: dirty.add(((p[0]//CHUNK)*CHUNK, (p[1]//CHUNK)*CHUNK))
        if phase in ('painting_in', 'painting_out'):
            for p in snap:
                dirty.add(((p[0]//CHUNK)*CHUNK, (p[1]//CHUNK)*CHUNK))

        for cy, cx in dirty:
            for y in range(cy, min(cy+CHUNK, h-1)):
                for x in range(cx, min(cx+CHUNK, w-1)):
                    p = (y, x)
                    if phase in ('painting_in', 'painting_out') and p in snap:
                        show = p in revealed if phase == 'painting_in' else p not in revealed
                        if show:
                            ch_, attr = snap[p]
                            try: scr.move(y, x); scr.addch(ch_, attr)
                            except curses.error: pass
                        elif p in frame:
                            c, col = frame[p]
                            try: scr.move(y, x); scr.addch(c, curses.color_pair(col)|(curses.A_BOLD if col>4 else 0))
                            except curses.error: pass
                        else:
                            try: scr.move(y, x); scr.addch(' ')
                            except curses.error: pass
                    elif p in overlay and phase not in ('painting_in', 'painting_out'):
                        ch_, attr = overlay[p]
                        try: scr.move(y, x); scr.addch(ch_, attr)
                        except curses.error: pass
                    elif p in frame:
                        c, col = frame[p]
                        try: scr.move(y, x); scr.addch(c, curses.color_pair(col)|(curses.A_BOLD if col>4 else 0))
                        except curses.error: pass
                    elif p in buf:
                        try: scr.move(y, x); scr.addch(' ')
                        except curses.error: pass

        bar_visible = show_help or opening == 'help' or closing == 'help'
        bar = f"  {AUTHOR}  ·  {VERSION} ".ljust(w) if bar_visible else " " * w
        for j, ch_ in enumerate(bar):
            if j < w-1:
                try: scr.move(h-1, j); scr.addch(ch_, curses.color_pair(2))
                except curses.error: pass

        buf = frame
        if dirty:
            dirty = set(); scr.refresh()
        time.sleep(0.016)

if __name__ == "__main__":
    import locale; locale.setlocale(locale.LC_ALL, '')
    try: curses.wrapper(main)
    except: pass
