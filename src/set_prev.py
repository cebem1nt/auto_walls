#!/usr/bin/env python3

from auto_walls import StateParser, ConfigParser, set_wallpaper, reset_state
import os, argparse


def main(state_dir: str, config_dir: str):

    state  = StateParser(state_dir).parse_state()
    c = ConfigParser(config_dir).parse_config()


    if len(state["wallpapers"]) == 0 or state["index"] <= 0 : # there is no wallpapers or
                                                              # allready first wallpaper

        wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])
        reset_state(wallpapers_dir, state_dir,  c["notify"])

        state  = StateParser(state_dir).parse_state()
        i = len(state["wallpapers"]) - 1 # going from the end

    else:
        i = state["index"] - 1  # setting wallpaper that was before 

    current_wallpaper = state["wallpapers"][i]
    set_wallpaper(c, state_dir, current_wallpaper, i)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="""
                                    A python wallpapers system subscript. 
                                    Sets the previous shuffled wallpaper. 
                                    Shufles and sets the last one if already first wallpaper.
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