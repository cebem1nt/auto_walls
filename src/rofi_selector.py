#!/usr/bin/env python3

from auto_walls import StateParser, ConfigParser, set_wallpaper
import subprocess, os, argparse


def main(state_dir: str, config_dir: str, theme:str):

    c = ConfigParser(config_dir).parse_config()
    state = StateParser(state_dir).parse_state()

    ws = state["wallpapers"]
    wd = os.path.expanduser(c["wallpapers_dir"])

    # Generate Rofi options with thumbnails
    rofi_options = "\n".join(f"{w.split("/")[-1]}\x00icon\x1f{w}" for w in ws)

    if len(theme) > 0: # checking argument
        rofi_theme = theme
    else:
        rofi_theme = c["rofi-theme"]
    
    # Launch Rofi with thumbnails and passed theme (none if empty)
    rofi_process = subprocess.Popen(f"rofi -dmenu -i -theme {rofi_theme}".split(),
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
        i = ws.index(selected_wallpaper_dir)
        set_wallpaper(c, state_dir, selected_wallpaper_dir, i)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="""
                                    A python wallpapers system subscript. 
                                    Runs rofi with list of shuffled wallpapers with tumbnails. 
                                    By default takes theme path from config file. 
                                    Theme can be passed as an argument, in this case it will have more priority than config's one.
                                    Additional info can be found at https://github.com/cebem1nt/auto_walls
                                """)

    p.add_argument('-c', '--config', 
                   help='Specify the config file', 
                   default='~/.config/auto_walls/config.json')
    
    p.add_argument('-s', '--state', 
                    help='Specify the state file', 
                    default='~/.auto_walls/state.json')

    p.add_argument('-t', '--theme', 
                    help='Specify the rofi theme file', 
                    default='')

    args = p.parse_args()
    main(state_dir=args.state, config_dir=args.config, theme=args.theme)
