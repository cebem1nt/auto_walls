#!/usr/bin/env python3

from auto_walls import ConfigParser, State, set_wallpaper
import os


def main(state_dir='~/.auto_walls/state.json', 
         config_dir='~/.config/auto_walls/config.json'):
    
    state = State(state_dir)
    c = ConfigParser(config_dir).parse_config()
    print(c)

    wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])

    if state.index == -2: # no state, first run
        state.reset_state(wallpapers_dir, c["notify"])
        i = 0

    else: #there are wallpapers 
        i = state.index + 1

        if i >= len(state.wallpapers):
            state.reset_state(wallpapers_dir, c["notify"])
            i = 0

    current_wallpaper = state.wallpapers[i]
        
    set_wallpaper(c, state, current_wallpaper, i)

if __name__ == '__main__':
    main()