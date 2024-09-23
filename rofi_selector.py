#!/usr/bin/env python3

from auto_walls import State, ConfigParser, set_wallpaper
import subprocess, os

if __name__ == '__main__':

    c = ConfigParser().parse_config()
    state = State()

    wd = os.path.expanduser(c["wallpapers_dir"])

    # Generate Rofi options with thumbnails
    rofi_options = "\n".join(f"{w.split("/")[-1]}\x00icon\x1f{w}" for w in state.wallpapers)

    # Launch Rofi with thumbnails and passed theme (none if empty)
    rofi_process = subprocess.Popen(f"rofi -dmenu -i  {'-theme ' + c["rofi-theme"]} -selected-row {state.index}".split(),
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)

    # Pass wallpapers with thumbnails to Rofi
    selected_option, _ = rofi_process.communicate(input=rofi_options)
    selected_option = selected_option.strip()

    # Check if a wallpaper was selected
    if selected_option:
        selected_wallpaper_dir = os.path.join(wd, selected_option.split('\x00icon\x1f')[0])  # Extract full wallpaper path
        i = state.wallpapers.index(selected_wallpaper_dir)
        set_wallpaper(c, state, selected_wallpaper_dir, i)