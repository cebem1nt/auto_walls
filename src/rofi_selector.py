#!/usr/bin/env python3

from auto_walls import StateParser, ConfigParser, set_wallpaper
import subprocess, os


def main(state_dir='~/.auto_walls/state.json', 
         config_dir='~/.config/auto_walls/config.json'):

    c = ConfigParser(config_dir).parse_config()
    state = StateParser(state_dir).parse_state()

    ws = state["wallpapers"]

    # Generate Rofi options with thumbnails
    rofi_options = "\n".join(f"{w.split("/")[-1]}\x00icon\x1f{w}" for w in ws)

    # -theme ~/Downloads/rofi-themes-collection/themes/rounded-common.rasi

    rofi_theme = c["rofi-theme"]
    
    # Launch Rofi with markup rows to display thumbnails
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
        selected_wallpaper_dir = os.path.join(os.path.expanduser(c["wallpapers_dir"]), selected_option.split('\x00icon\x1f')[0])  # Extract full wallpaper path
        set_wallpaper(c["wallpapers_cli"], selected_wallpaper_dir, 
                      ws.index(selected_wallpaper_dir), state_dir, 
                      c["change_backlight"], c["backlight_transition"])

if __name__ == "__main__":
    main()

