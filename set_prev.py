#!/usr/bin/env python3

from auto_walls import get_config, State, set_wallpaper
import os

if __name__ == '__main__':
    state = State()
    c = get_config()

    if not state.wallpapers or (state.index <= 0): # there is no wallpapers or allready first wallpaper
        state.reset_state(os.path.expanduser(c["wallpapers_dir"]), c["notify"])

        i = len(state.wallpapers) - 1 # going from the end

    else:
        i = state.index - 1  # setting wallpaper that was before 

    current_wallpaper = state.wallpapers[i]
    set_wallpaper(c, state, current_wallpaper, i)