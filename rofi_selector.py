#!/usr/bin/env python3

from auto_walls import State, ConfigParser, set_wallpaper
import subprocess, os, argparse


def main(theme:str, config_dir='~/.config/auto_walls/config.json'):

    c = ConfigParser(config_dir).parse_config()
    state = State()

    wd = os.path.expanduser(c["wallpapers_dir"])

    # Generate Rofi options with thumbnails
    rofi_options = "\n".join(f"{w.split("/")[-1]}\x00icon\x1f{w}" for w in state.wallpapers)

    if len(theme) > 0: # checking argument
        rofi_theme = theme
    else:
        rofi_theme = c["rofi-theme"]
    
    # Launch Rofi with thumbnails and passed theme (none if empty)
    rofi_process = subprocess.Popen(f"rofi -dmenu -i -theme {rofi_theme} -selected-row {state.index}".split(),
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

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="""
                                    Runs rofi with list of shuffled wallpapers with tumbnails. 
                                    By default takes theme path from the config file. 
                                    Theme can be passed as an argument, in this case it will have more priority than config's one.
                                    Additional info can be found at https://github.com/cebem1nt/auto_walls
                                """)

    p.add_argument('-t', '--theme', 
                    help='Specify the rofi theme file', 
                    default='')

    args = p.parse_args()
    main(theme=args.theme)
