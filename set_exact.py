#!/usr/bin/env python3

from auto_walls import AutoWalls 
import sys

if __name__ == '__main__':
    aw = AutoWalls()
    aw.set_wallpaper(sys.argv[-1], -1, do_change_index=False)