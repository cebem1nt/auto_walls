#!/usr/bin/env python3

from auto_walls import AutoWalls

if __name__ == '__main__':
    aw = AutoWalls()

    if aw.index <= 0: # allready first wallpaper
        aw.reset_state()
        i = len(aw.wallpapers) - 1 # going from the end

    else:
        i = aw.index - 1  # setting wallpaper that was before 

    aw.set_wallpaper(aw.wallpapers[i], i)