#!/usr/bin/env python3

from auto_walls import ConfigParser, State, set_wallpaper
import os

if __name__ == '__main__':
    state = State()
    c = ConfigParser().parse_config()

    if len(state.wallpapers) == 0 or state.index <= 0 : # there is no wallpapers or
                                                        # allready first wallpaper

        wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])
        state.reset_state(wallpapers_dir, c["notify"])

        i = len(state.wallpapers) - 1 # going from the end

    else:
        i = state.index - 1  # setting wallpaper that was before 

    current_wallpaper = state.wallpapers[i]
    set_wallpaper(c, state, current_wallpaper, i)