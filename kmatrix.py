#!/usr/bin/env python3
import curses, random, math, time

CHARS = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789"

class Drop:
    def __init__(self, x, h):
        self.x, self.y, self.spd, self.len = x, float(random.randint(-h, -1)), random.uniform(0.3, 1.5), random.randint(5, 20)
        self.chars = [random.choice(CHARS) for _ in range(self.len)]

    def update(self, h, speed=1.0, reverse=False):
        self.y += self.spd * speed * (-1 if reverse else 1)
        if (reverse and self.y + self.len < 0) or (not reverse and self.y - self.len > h):
            self.y, self.spd = (float(random.randint(h+1, h+20)) if reverse else float(random.randint(-20, -1))), random.uniform(0.5, 1.8)
            self.chars = [random.choice(CHARS) for _ in range(self.len)]

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
    if curses.has_colors():
        curses.start_color(); curses.use_default_colors()
        for i, c in enumerate(THEMES[0], 1): curses.init_pair(i, c, -1)

    h, w = scr.getmaxyx()
    CHUNK=8
    drops, buf, speed, theme, paused, reverse = [Drop(x, h) for x in range(w)], {}, 1.0, 0, False, False
    dirty={((y//CHUNK)*CHUNK, (x//CHUNK)*CHUNK) for y in range(h) for x in range(w)}

    while True:
        nh, nw = scr.getmaxyx()
        if nh != h or nw != w:
            h, w, drops, buf = nh, nw, [Drop(x, h) for x in range(w)], {}
            dirty={((y//CHUNK)*CHUNK, (x//CHUNK)*CHUNK) for y in range(h) for x in range(w)}
            scr.clear()

        ch = scr.getch()
        if ch in (ord('q'), ord('Q'), 27): break
        if ch in (ord('+'), ord('=')): speed = min(3.0, speed + 0.2)
        if ch in (ord('-'), ord('_')): speed = max(0.2, speed - 0.2)
        if ch in (ord('c'), ord('C')):
            theme = (theme + 1) % len(THEMES)
            for i, c in enumerate(THEMES[theme], 1): curses.init_pair(i, c, -1)
        if ch in (ord(' '),): paused = not paused
        if ch in (ord('r'), ord('R')): reverse = not reverse
        if ch == curses.KEY_RESIZE: continue

        if paused: time.sleep(0.016); continue

        frame = {}
        for d in drops:
            d.update(h, speed, reverse)
            for i in range(d.len):
                y = int(d.y - i * (1 if not reverse else -1))
                if 0 <= y < h-1 and 0 <= d.x < w-1:
                    col = 6 if i == 0 else 5 if i < 3 else 4 if i < 6 else 3 if i < d.len * 0.6 else 2
                    frame[(y, d.x)] = (d.chars[i], col)

        for p in frame:
            if buf.get(p) != frame[p]: dirty.add(((p[0]//CHUNK)*CHUNK, (p[1]//CHUNK)*CHUNK))
        for p in buf:
            if p not in frame: dirty.add(((p[0]//CHUNK)*CHUNK, (p[1]//CHUNK)*CHUNK))

        for cy, cx in dirty:
            for y in range(cy, min(cy+CHUNK, h-1)):
                for x in range(cx, min(cx+CHUNK, w-1)):
                    p = (y, x)
                    if p in frame:
                        c, col = frame[p]
                        try: scr.move(y, x); scr.addch(c, curses.color_pair(col)|(curses.A_BOLD if col>4 else 0))
                        except: pass
                    elif p in buf:
                        try: scr.move(y, x); scr.addch(' ')
                        except: pass

        buf = frame; dirty = set(); scr.refresh(); time.sleep(0.016)

if __name__ == "__main__":
    import locale; locale.setlocale(locale.LC_ALL, '')
    try: curses.wrapper(main)
    except: pass
