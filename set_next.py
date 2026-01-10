#!/usr/bin/env python3

from auto_walls import AutoWalls

if __name__ == '__main__':
    aw = AutoWalls()
    do_notify = aw.config["notify"]

    i = aw.index + 1

    if i >= len(aw.wallpapers):
        aw.reset_state()
        i = 0

    aw.set_wallpaper(aw.wallpapers[i], i)