#!/usr/bin/env python3

from auto_walls import StateParser, ConfigParser, reset_state, set_wallpaper
import os, argparse


def main(state_dir: str, config_dir: str):
    
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
    p = argparse.ArgumentParser(description="""
                                    A python wallpapers system subscript. 
                                    Sets the next shuffled wallpaper. Shuffles them if already the last one.
                                    Additional info can be found at https://github.com/cebem1nt/auto_walls
                                """)

    p.add_argument('-c', '--config', 
                   help='Specify the config file', 
                   default='~/.config/auto_walls/config.json')
    
    p.add_argument('-s', '--state', 
                    help='Specify the state file', 
                    default='~/.auto_walls/state.json')

    args = p.parse_args()
    main(state_dir=args.state, config_dir=args.config)