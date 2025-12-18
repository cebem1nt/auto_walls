#!/usr/bin/env python3

from auto_walls import State, get_config, set_wallpaper, expand_path
import subprocess, os

def get_wallpaper_thumbnail(wallpaper_file: str, wallpaper_name: str, max_size=500, quality=5):
    cache_dir = os.path.expanduser('~/.cache/auto_walls/thumbnails')
    wallpaper_thumbnail = os.path.join(cache_dir, wallpaper_name)

    os.makedirs(cache_dir, exist_ok=True)

    if os.path.exists(wallpaper_thumbnail):
        return wallpaper_thumbnail

    else:
        subprocess.run([
                    "ffmpeg", 
                    "-i", wallpaper_file, 
                    "-vf", f"scale='if(gt(iw,ih),{max_size},-1)':'if(gt(iw,ih),-1,{max_size})'", 
                    "-frames:v", "1", 
                    "-q:v", str(quality), 
                    wallpaper_thumbnail
                ])
        return wallpaper_thumbnail

if __name__ == '__main__':

    c = get_config()
    state = State()

    wd = expand_path(c["wallpapers_dir"])

    # Generate Rofi options with thumbnails
    rofi_options = ""

    if sum(1 for entry in os.scandir(wd) if entry.is_file()) != len(state.wallpapers):
        state.reset_state(wd, c["notify"]) 

    for wallpaper_file in state.wallpapers:
        wallpaper_name = wallpaper_file.split("/")[-1]
        wallpaper_thumbnail = get_wallpaper_thumbnail(wallpaper_file, wallpaper_name)

        rofi_options += f"{wallpaper_name}\x00icon\x1f{wallpaper_thumbnail}\n"

    # Launch Rofi with thumbnails and passed theme (none if empty)
    rofi_theme =  "-theme " + c["rofi_theme"] if c["rofi_theme"] else ' '
    
    rofi_process = subprocess.Popen(["rofi", "-sync", "-dmenu", "-i"] + rofi_theme.split() + ["-selected-row", str(state.index)],
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
        if i != state.index:
            set_wallpaper(c, state, selected_wallpaper_dir, i)
