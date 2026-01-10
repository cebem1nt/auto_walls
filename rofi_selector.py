#!/usr/bin/env python3

import subprocess, os, signal, sys
from auto_walls import AutoWalls, expand_path

def get_wallpaper_thumbnail(
    wallpaper_file: str, 
    wallpaper_name: str, 
    max_size=500, 
    quality=5
):
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

def generate_all_thumbnails(aw: AutoWalls):
    for wallpaper_file in aw.wallpapers:
        wallpaper_name = wallpaper_file.split("/")[-1]
        get_wallpaper_thumbnail(wallpaper_file, wallpaper_name)

if __name__ == '__main__':
    aw = AutoWalls()

    if sys.argv[-1] == "--gen-thumbnails":
        generate_all_thumbnails(aw)
        sys.exit(0)

    rofi_theme = aw.config["rofi_theme"] if aw.config["rofi_theme"] else ' '

    if aw.has_new_wallpapers():
        aw.reset_state()

    opts = ""
    prev = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGTERM, signal.SIG_IGN) # Ignore sigterm in this section

    for wallpaper_file in aw.wallpapers:
        wallpaper_name = wallpaper_file.split("/")[-1]
        wallpaper_thumbnail = get_wallpaper_thumbnail(wallpaper_file, wallpaper_name)

        opts += f"{wallpaper_name}\x00icon\x1f{wallpaper_thumbnail}\n"

    signal.signal(signal.SIGTERM, prev)

    rofi_process = subprocess.Popen(
        ["rofi", "-dmenu", "-i", "-selected-row", str(aw.index), "-theme", rofi_theme],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Pass wallpapers with thumbnails to Rofi
    rofi_process.stdin.write(opts)
    selected_option, _ = rofi_process.communicate()
    selected_option = selected_option.strip()

    # Check if a wallpaper was selected
    if selected_option:
        wallpaper = selected_option.split('\x00icon\x1f')[0] # Extract wallpaper path
        selected_wallpaper_dir = os.path.join(aw.wallpapers_dir, wallpaper)
        
        i = aw.wallpapers.index(selected_wallpaper_dir)
        aw.set_wallpaper(selected_wallpaper_dir, i)
