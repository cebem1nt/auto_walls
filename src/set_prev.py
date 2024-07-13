#!/usr/bin/env python3

from auto_walls import StateParser, ConfigParser, set_wallpaper, reset_state
import os, subprocess


def main(state_dir='~/.auto_walls/state.json',
         config_dir='~/.config/auto_walls/config.json'):

    state  = StateParser(state_dir).parse_state()
    c = ConfigParser(config_dir).parse_config()


    if len(state["wallpapers"]) == 0 or state["index"] <= 0 : # there are no wallpapers or
                                                              # allready first wallpaper
        wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])
        reset_state(wallpapers_dir, state_dir,  c["notify"])

        state  = StateParser(state_dir).parse_state()
        i = len(state["wallpapers"]) - 1 # going from the end

    else:
        i = state["index"] - 1  # setting wallpaper that was before 

    current_wallpaper = state["wallpapers"][i]
    set_wallpaper(c["wallpapers_cli"], current_wallpaper, i, state_dir, c["change_backlight"], c["backlight_transition"])


if __name__ == '__main__':
    main()