#!/usr/bin/env python3

from auto_walls import get_config, State, set_wallpaper
import os

if __name__ == '__main__':
    state = State()
    c = get_config()

    wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])

    if state.index is None: # no state, first run
        state.reset_state(wallpapers_dir, c["notify"])
        i = 0

    else: #there are wallpapers 
        i = state.index + 1

        if i >= len(state.wallpapers):
            state.reset_state(wallpapers_dir, c["notify"])
            i = 0

    current_wallpaper = state.wallpapers[i]
    
    set_wallpaper(c, state, current_wallpaper, i)