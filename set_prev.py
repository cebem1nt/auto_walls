#!/usr/bin/env python3

from auto_walls import StateParser, ConfigParser, State, set_wallpaper
import os


def main(state_dir='~/.auto_walls/state.json', 
         config_dir='~/.config/auto_walls/config.json'):

    state = State(state_dir)
    c = ConfigParser(config_dir).parse_config()

    if len(state.wallpapers) == 0 or state.index <= 0 : # there is no wallpapers or
                                                        # allready first wallpaper

        wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])
        state.reset_state(wallpapers_dir, c["notify"])

        i = len(state.wallpapers) - 1 # going from the end

    else:
        i = state.index - 1  # setting wallpaper that was before 

    current_wallpaper = state.wallpapers[i]
    set_wallpaper(c, state, current_wallpaper, i)

if __name__ == '__main__':
    main()