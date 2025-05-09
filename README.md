# Auto walls
**When using a window manager, wallpapers is a part of it. Maybe you want a menu to choose wallpaper, shuffling, automatically change them, match keyboard backlight to wallpaper's best color, setting next/previous. If so, this is what you're looking for! Auto walls is a Linux wallpaper system for any window manager: flexible and customizable, written entirely in Python.**

## Features

- Automatically sets random wallpaper every n minutes.
- Sets keyboard backlight color based on the wallpaper.
- Provides scripts for setting previous and next wallpapers.
- Provides Rofi menu script to select wallpaper.

## About

A collection of scripts including a main script launched at startup, scripts to set previous and next wallpapers, a script to run a Rofi menu with wallpaper options, and adaptive keyboard backlight module. If `change_backlight` in the config is set to true, the backlight changes based on the dominant color from the wallpaper image. Initially used with `swww` and `rogauracore` (ASUS ROG laptops) to changie wallpaper and keyboard backlight color, but can be configured to use with any other cli tool

## Default Requirements

- [swww](https://github.com/LGFae/swww): Wayland wallpapers tool.
- [rogauracore](https://github.com/wroberts/rogauracore): CLI tool for changing keyboard color on ASUS ROG laptops.
- [rofi](https://github.com/davatorium/rofi): Required for the wallpapers menu.
- [ffmpeg](https://github.com/FFmpeg/FFmpeg): For thumbnails generation

## Python Libraries

### pip

```bash
pip install numpy Pillow scikit-learn
```

### Arch Linux

```bash
sudo pacman -S python-numpy python-scikit-learn python-pillow
```

## Usage

Clone this repository and execute the main script (`auto_walls.py`) on startup with your window manager. It will change wallpapers at specified intervals and provide functions for dynamic backlight color and setting next/previous wallpapers. Bind `set_next.py` and `set_previous.py` for controlling wallpaper changes and `rofi_selector.py` for toggling the wallpaper menu.

## Example on Hyprland:

```ini
exec-once = python3 ~/your/path/to/auto_walls/auto_walls.py

bind = ALT, F5,       exec, python3 ~/your/path/to/auto_walls/set_next.py
bind = ALT SHIFT, F5, exec, python3 ~/your/path/to/auto_walls/set_prev.py

bind = SUPER, Y, exec, python3 ~/your/path/to/auto_walls/rofi_selector.py
```

> **Note:** It's strongly recommended to run `auto_walls.py` from the terminal for the first time.

## Example Config

After the first run of `auto_walls.py`, the following config will be generated at `~/.config/auto_walls/config.json` by default:

```json
{
    "interval": 30,
    "wallpapers_dir": "~/Pictures",
    "wallpapers_cli": "swww img <picture>",
    "keyboard_cli": "rogauracore single_static <color>",
    "keyboard_transition_cli": "rogauracore single_breathing <prev> <color> 3",
    "change_backlight": false,
    "transition_duration": 1.1,
    "notify": true,
    "backlight_transition": false,
    "rofi_theme": ""
}
```

- **"interval"**: Time interval in minutes for changing wallpapers. Set to 0 to disable automatic wallpaper changes.
- **"wallpapers_dir"**: Directory where wallpapers are stored.
- **"wallpapers_cli"**: Command to set wallpaper (`<picture>` is placeholder for wallpaper path). Can be customized; for example, for `feh`, use `feh --bg-fill <picture> `.
- **"keyboard_cli"**: Command to change keyboard color (`<color>` is placeholder).
- **"keyboard_transition_cli"**: Command for transitioning keyboard backlight color. Example simulates a breathing effect (`<prev>` represents previous color and `<color>` is new color).
- **"transition_duration"**: Transition duration in seconds. 
- **"change_backlight"**: Enable/disable keyboard backlight changes.
- **"notify"**: Enable/disable notifications.
- **"backlight_transition"**: Enable/disable backlight transition effects.
- **"rofi-theme"**: Path to a custom Rofi theme when using `rofi_selector.py`; leave empty for default theme..

## TODO
This code is so ugly and complicated. Rework someday