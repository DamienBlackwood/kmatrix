#!/usr/bin/env python3
import curses, random, time, json, os, atexit

CONFIG_PATH = os.path.expanduser("~/.kmatrix")
state = {"theme": 0, "speed": 1.0, "reverse": False, "mutate": False, "sparse": False, "long": False}

def load_config():
    try:
        with open(CONFIG_PATH) as f:
            d = json.load(f)
        return (d.get("theme", 0), d.get("speed", 1.0), d.get("reverse", False),
                d.get("mutate", False), d.get("sparse", False), d.get("long", False))
    except:
        return 0, 1.0, False, False, False, False

def save_config():
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(state, f)
    except:
        pass

atexit.register(save_config)

CHARS = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789"

AUTHOR  = "github.com/DamienBlackwood"
VERSION = "v0.3"

class Drop:
    def __init__(self, x, h, long=False):
        self.x = x
        self.len = random.randint(30, 60) if long else random.randint(5, 20)
        self.spd = random.uniform(0.3, 1.5)
        self.y = float(random.randint(-h, -1))
        self.acc = random.random()
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
        self.acc = random.random()

    def update(self, h, speed=1.0, mutate=False):
        if self.flip_delay > 0:
            self.flip_delay -= 1
        else:
            self.dir += (self.target_dir - self.dir) * 0.08

        self.acc += self.spd * speed
        steps = int(self.acc)
        self.acc -= steps
        self.y += steps * self.dir

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

    theme, speed, reverse, cfg_mutate, cfg_sparse, cfg_long = load_config()
    state["theme"] = theme; state["speed"] = speed; state["reverse"] = reverse
    state["mutate"] = cfg_mutate; state["sparse"] = cfg_sparse; state["long"] = cfg_long

    ATTR = [0] * 7
    def refresh_attr():
        for i in range(1, 7):
            ATTR[i] = curses.color_pair(i) | (curses.A_BOLD if i > 4 else 0)

    if curses.has_colors():
        curses.start_color(); curses.use_default_colors()
        for i, c in enumerate(THEMES[theme], 1): curses.init_pair(i, c, -1)
    refresh_attr()

    def detect_fps_env():
        env = os.environ.get("KMATRIX_FPS")
        if env:
            try:
                return 1.0 / max(1, min(240, int(env)))
            except ValueError:
                pass
        fast = ("alacritty", "kitty", "ghostty", "wezterm", "rio")
        term = os.environ.get("TERM", "")
        prog = os.environ.get("TERM_PROGRAM", "")
        low = term.lower() + prog.lower()
        if any(t in low for t in fast):
            return 1.0 / 120
        return 1.0 / 60

    h, w = scr.getmaxyx()
    TARGET_FRAME_TIME = detect_fps_env()

    paused = False
    show_help, show_exp = False, False
    mutate = state.get("mutate", False)
    density_sparse = state.get("sparse", False)
    long_mode = state.get("long", False)

    phase = None
    direction = None
    snap = {}
    revealed = set()
    closing = None
    opening = None
    transition_gen = 0
    transition_delay = 0
    force_dense = False

    drops = make_drops(w, h)
    last_drawn = {}

    overlay_cache = None
    overlay_cache_key = None
    def get_overlay():
        nonlocal overlay_cache, overlay_cache_key
        key = (show_help, show_exp, h, w, mutate, density_sparse, long_mode)
        if key != overlay_cache_key:
            overlay_cache = build_overlay(show_help, show_exp)
            overlay_cache_key = key
        return overlay_cache

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

    def get_exp_help():
        return [
            ("", ""),
            ("  experimental settings", ""),
            ("", ""),
            (f"  m  [{'on' if mutate else 'off'}]", "character mutation"),
            (f"  d  [{'on' if density_sparse else 'off'}]", "sparse density"),
            (f"  x  [{'on' if long_mode else 'off'}]", "long trails"),
            ("", ""),
            ("  h",   "toggle this panel"),
            ("", ""),
        ]

    def build_overlay(show_h, show_e):
        pw = 44
        cells = {}
        exp_rows = get_exp_help()
        for rows in ([HELP] if show_h else []) + ([exp_rows] if show_e else []):
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
        nonlocal phase, direction, snap, revealed, closing, opening, transition_gen, transition_delay, force_dense
        transition_gen += 1
        transition_delay = 12
        phase = 'delay'
        direction = dir_
        force_dense = True
        sh = show_h or (open_which == 'help')
        se = show_e or (open_which == 'exp')
        snap = build_overlay(sh, se)
        revealed = set()
        closing = close_which
        opening = open_which
        for d in drops:
            d.born_gen = transition_gen - 1
            if d.dir >= 0:
                completely_off = d.y < 0 or d.y - d.len > h
            else:
                completely_off = d.y > h or d.y + d.len < 0
            if completely_off:
                d.active = True

    while True:
        nh, nw = scr.getmaxyx()
        if nh != h or nw != w:
            h, w = nh, nw
            drops = make_drops(w, h)
            last_drawn = {}
            phase = None; direction = None; snap = {}; revealed = set(); closing = None; opening = None
            overlay_cache = None
            scr.clear()

        ch = scr.getch()
        if ch in (ord('q'), ord('Q'), 27): break
        if ch in (ord('+'), ord('=')): speed = min(3.0, speed + 0.2); state["speed"] = speed
        if ch in (ord('-'), ord('_')): speed = max(0.2, speed - 0.2); state["speed"] = speed
        if ch in (ord('c'), ord('C')):
            theme = (theme + 1) % len(THEMES); state["theme"] = theme
            for i, c in enumerate(THEMES[theme], 1): curses.init_pair(i, c, -1)
            refresh_attr()
        if ch in (ord(' '),): paused = not paused
        if ch in (ord('r'), ord('R')):
            reverse = not reverse; state["reverse"] = reverse
            for d in drops: d.set_target(-1.0 if reverse else 1.0)
        if phase is None:
            if ch in (ord('?'),):
                if not show_help: start_transition('in', show_help, show_exp, open_which='help')
                else: start_transition('out', show_help, show_exp, close_which='help')
            if ch in (ord('h'), ord('H')):
                if not show_exp: start_transition('in', show_help, show_exp, open_which='exp')
                else: start_transition('out', show_help, show_exp, close_which='exp')
        if ch in (ord('m'), ord('M')):
            mutate = not mutate; state["mutate"] = mutate
        if ch in (ord('d'), ord('D')):
            density_sparse = not density_sparse; state["sparse"] = density_sparse
        if ch in (ord('x'), ord('X')):
            long_mode = not long_mode; state["long"] = long_mode
        if ch == curses.KEY_RESIZE: continue

        if paused:
            time.sleep(max(0.005, TARGET_FRAME_TIME))
            continue

        frame_start = time.perf_counter()

        in_transition = phase is not None
        use_long = long_mode or in_transition

        frame = {}
        for d in drops:
            mutated, expired = d.update(h, speed, mutate)
            if expired:
                d.len = random.randint(30, 60) if use_long else random.randint(5, 20)
                d.spd = random.uniform(0.5, 1.8)
                d.y = float(random.randint(-20, -1)) if d.target_dir >= 0 else float(random.randint(h+1, h+20))
                d.chars = [random.choice(CHARS) for _ in range(d.len)]
                d.born_gen = transition_gen
                if force_dense or not density_sparse:
                    d.active = True
                else:
                    d.active = random.random() < 0.35
            if not d.active:
                continue

            if not (0 <= d.x < w - 1):
                continue

            d_len = d.len
            sign = 1 if d.dir >= 0 else -1
            d_y = int(d.y)

            if sign == 1:
                i_start = max(0, d_y - (h - 2))
                i_end = min(d_len, d_y + 1)
            else:
                i_start = max(0, -d_y)
                i_end = min(d_len, h - 1 - d_y)

            if i_start >= i_end:
                continue

            if phase in ('waiting', 'painting_in', 'painting_out') and d.born_gen == transition_gen:
                head_pos = (d_y, d.x)
                if head_pos in snap and head_pos not in revealed:
                    revealed.add(head_pos)
                    if phase == 'waiting':
                        phase = 'painting_in' if direction == 'in' else 'painting_out'

            for i in range(i_start, i_end):
                y = d_y - i * sign
                col = 6 if i == 0 else 5 if i < 3 else 4 if i < 6 else 3 if i < d_len * 0.6 else 2
                frame[(y, d.x)] = (d.chars[i], ATTR[col])

        if phase == 'delay':
            transition_delay -= 1
            if transition_delay <= 0:
                phase = 'waiting'

        if phase in ('painting_in', 'painting_out') and snap and revealed >= set(snap.keys()):
            if opening == 'help': show_help = True
            if opening == 'exp':  show_exp  = True
            if closing == 'help': show_help = False
            if closing == 'exp':  show_exp  = False
            phase = None; direction = None; snap = {}; revealed = set(); closing = None; opening = None
            force_dense = False

        overlay = get_overlay()

        target = dict(frame)
        if phase == 'painting_in' and snap:
            for p in revealed:
                target[p] = snap[p]
        elif phase == 'painting_out' and snap:
            for p in snap:
                if p not in revealed:
                    target[p] = snap[p]
        elif overlay:
            target.update(overlay)

        bar_visible = show_help or opening == 'help' or closing == 'help'
        if bar_visible:
            left = f"  {VERSION}"
            right = f"{AUTHOR}  "
            pad = max(2, w - 1 - len(left) - len(right))
            bar_text = left + " " * pad + right
            bar_attr = ATTR[2]
        else:
            bar_text = ' ' * (w - 1)
            bar_attr = ATTR[2]

        for j, ch_ in enumerate(bar_text):
            if j < w - 1:
                target[(h - 1, j)] = (ch_, bar_attr)

        for p, val in target.items():
            if last_drawn.get(p) != val:
                try:
                    scr.addch(p[0], p[1], val[0], val[1])
                except curses.error:
                    pass

        for p in last_drawn:
            if p not in target:
                try:
                    scr.addch(p[0], p[1], ' ', bar_attr)
                except curses.error:
                    pass

        if target != last_drawn:
            last_drawn = dict(target)
            scr.noutrefresh()
            curses.doupdate()

        elapsed = time.perf_counter() - frame_start
        sleep_time = TARGET_FRAME_TIME - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

def main_wrapper():
    import locale; locale.setlocale(locale.LC_ALL, '')
    try: curses.wrapper(main)
    except (KeyboardInterrupt, Exception): pass

if __name__ == "__main__":
    main_wrapper()
