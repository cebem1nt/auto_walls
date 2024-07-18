#!/usr/bin/env python3

from auto_walls import StateParser, ConfigParser, reset_state, set_wallpaper
import os


def main(state_dir='~/.auto_walls/state.json', 
         config_dir='~/.config/auto_walls/config.json'):
    
    while True:
        state  = StateParser(state_dir).parse_state()
        c = ConfigParser(config_dir).parse_config()

        wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])

        if state["index"] == -2: # no state, first run
            reset_state(wallpapers_dir, state_dir, c["notify"])
            continue

        else: #there are wallpapers 
            i = state["index"]+1
            try:
                current_wallpaper = state["wallpapers"][i]

            except: #index out of range
                reset_state(wallpapers_dir, state_dir, c["notify"])
                continue
            
        set_wallpaper(c, state_dir, current_wallpaper, i)
        break

if __name__ == '__main__':
    main()