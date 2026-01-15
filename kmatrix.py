#!/usr/bin/env python3
import curses, random, math, time

CHARS = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789"

class Drop:
    def __init__(self, x, h):
        self.x, self.y, self.spd, self.len = x, random.randint(-h, -1), random.uniform(0.5, 2.0), random.randint(5, 20)

    def update(self, h, speed=1.0, reverse=False):
        self.y += self.spd * speed * (-1 if reverse else 1)
        if (reverse and self.y + self.len < 0) or (not reverse and self.y - self.len > h):
            self.y, self.spd = (random.randint(h+1, h+20) if reverse else random.randint(-20, -1)), random.uniform(0.5, 2.0)

class Vortex:
    def __init__(self, w, h):
        self.t, self.w, self.h = 0, w, h

    def get_pos(self, i):
        a = self.t + i * 0.3
        r = (self.t * 0.5 + i * 0.8) % min(self.w/2, self.h)
        return int(self.w/2 + r * math.cos(a)), int(self.h/2 + r * math.sin(a) * 0.5), int(i % len(CHARS))

    def update(self, speed=1.0):
        self.t += 0.15 * speed

def main(scr):
    curses.curs_set(0); scr.nodelay(1); scr.timeout(0)
    THEMES = [[232,22,28,34,46,226,51,201], [17,18,19,20,21,226,51,201], [52,88,124,160,196,226,51,201], [53,89,125,161,197,226,51,201]]
    if curses.has_colors():
        curses.start_color(); curses.use_default_colors()
        for i, c in enumerate(THEMES[0], 1): curses.init_pair(i, c, -1)

    h, w = scr.getmaxyx()
    drops, vortex, mode, buf, speed, theme, paused, reverse = [Drop(x, h) for x in range(w)], Vortex(w, h), 0, {}, 1.0, 0, False, False

    while True:
        nh, nw = scr.getmaxyx()
        if nh != h or nw != w:
            h, w, drops, vortex, buf = nh, nw, [Drop(x, h) for x in range(w)], Vortex(w, h), {}
            scr.clear()

        ch = scr.getch()
        if ch in (ord('q'), ord('Q'), 27): break
        if ch in (ord('v'), ord('V')): mode = 1 - mode
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
        if mode == 0:
            for d in drops:
                d.update(h, speed, reverse)
                for i in range(d.len):
                    y = int(d.y - i * (1 if not reverse else -1))
                    if 0 <= y < h-1 and 0 <= d.x < w-1:
                        col = 6 if i == 0 else 5 if i < 3 else 4 if i < 6 else 3 if i < d.len * 0.6 else 2
                        frame[(y, d.x)] = (random.choice(CHARS), col)
        else:
            vortex.update(speed)
            for i in range(80):
                x, y, ci = vortex.get_pos(i)
                if 0 <= y < h-1 and 0 <= x < w-1: frame[(y, x)] = (CHARS[ci], 7 if i % 2 else 8)

        for pos in set(buf) - set(frame):
            try: scr.addstr(pos[0], pos[1], ' ')
            except: pass
        for pos, (c, col) in frame.items():
            if buf.get(pos) != (c, col):
                try: scr.addstr(pos[0], pos[1], c, curses.color_pair(col) | (curses.A_BOLD if col > 4 else 0))
                except: pass

        buf = frame; scr.refresh(); time.sleep(0.016)

if __name__ == "__main__":
    import locale; locale.setlocale(locale.LC_ALL, '')
    try: curses.wrapper(main)
    except: pass
