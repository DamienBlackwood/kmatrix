#!/usr/bin/env python3
import curses, random, time

CHARS = "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789"

def main(scr):
    curses.curs_set(0)
    scr.nodelay(1)

    THEMES = [
        [232,22,28,34,46,40], [17,18,19,20,21,27], [52,88,124,160,196,202],
        [53,89,125,161,197,171], [235,238,241,245,249,255], [54,91,128,165,201,219]
    ]
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        for i, c in enumerate(THEMES[0], 1):
            curses.init_pair(i, c, -1)

    h, w = scr.getmaxyx()
    maxh, maxw = h - 1, w - 1

    def build_colors():
        c = [curses.color_pair(i) for i in range(1, 7)]
        cb = [c[4] | curses.A_BOLD, c[5] | curses.A_BOLD]
        return c, cb
    colors, colors_bold = build_colors()

    # Drops: [x, y, speed, length, chars[]]
    # Spread across columns, ~60% density
    def make_drops(w, h):
        return [[x, random.uniform(-h, 0), random.uniform(0.4, 1.3), random.randint(5, 14),
                 [random.randint(0, len(CHARS)-1) for _ in range(18)]]
                for x in range(w) if random.random() < 0.6]

    drops = make_drops(maxw, maxh)
    prev_cells = set()  # Track cells that had content last frame
    speed, theme, paused, reverse = 1.0, 0, False, False

    while True:
        nh, nw = scr.getmaxyx()
        nh -= 1; nw -= 1
        if nh != maxh or nw != maxw:
            maxh, maxw = nh, nw
            drops = make_drops(maxw, maxh)
            prev_cells = set()
            scr.clear()

        ch = scr.getch()
        if ch in (ord('q'), ord('Q'), 27): break
        if ch in (ord('+'), ord('=')): speed = min(3.0, speed + 0.2)
        if ch in (ord('-'), ord('_')): speed = max(0.2, speed - 0.2)
        if ch in (ord('c'), ord('C')):
            theme = (theme + 1) % len(THEMES)
            for i, c in enumerate(THEMES[theme], 1):
                curses.init_pair(i, c, -1)
            colors, colors_bold = build_colors()
        if ch == ord(' '): paused = not paused
        if ch in (ord('r'), ord('R')): reverse = not reverse

        if paused:
            time.sleep(0.03)
            continue

        curr_cells = set()
        addch = scr.addch  # Local reference for speed

        for d in drops:
            x, y, spd, length, chars = d
            y += spd * speed * (-1 if reverse else 1)
            d[1] = y

            if (reverse and y + length < 0) or (not reverse and y - length > maxh):
                d[1] = random.uniform(maxh, maxh + 12) if reverse else random.uniform(-12, 0)
                d[2] = random.uniform(0.4, 1.3)
                d[3] = random.randint(5, 14)
                continue

            iy = int(y)
            for i in range(length):
                py = iy - i if not reverse else iy + i
                if 0 <= py < maxh:
                    curr_cells.add((py, x))
                    ci = chars[i % len(chars)]
                    ch_out = CHARS[ci]
                    if i == 0:
                        attr = colors_bold[1]
                    elif i < 2:
                        attr = colors_bold[0]
                    elif i < 4:
                        attr = colors[3]
                    elif i < length >> 1:
                        attr = colors[2]
                    else:
                        attr = colors[1]
                    try: addch(py, x, ch_out, attr)
                    except: pass

        # Clear cells that are no longer occupied
        for cell in prev_cells - curr_cells:
            try: addch(cell[0], cell[1], ' ')
            except: pass

        prev_cells = curr_cells
        scr.refresh()
        time.sleep(0.016)

if __name__ == "__main__":
    import locale
    locale.setlocale(locale.LC_ALL, '')
    try: curses.wrapper(main)
    except KeyboardInterrupt: pass
