# Auto walls

Auto walls is a Linux wallpaper system for any window manager: flexible and customizable, written entirely in Python.

## Features

- Automatically changes wallpapers.
- Sets keyboard backlight color based on the wallpaper.
- Provides scripts for setting previous and next wallpapers.
- Supports Rofi menu with thumbnails of wallpapers.

## About

A collection of scripts including a main script launched at startup, scripts to set previous and next wallpapers, a script to run a Rofi menu with wallpaper options, and a keyboard module. If `change_backlight` in the config is set to true, the backlight changes based on the dominant color from the wallpaper image. Initially designed for `swww` and `rogauracore` (ASUS ROG laptops) due to their CLI interfaces for changing wallpaper and keyboard backlight color, but adaptable to any other CLI tools for similar tasks.

## Default Requirements

- [swww](https://github.com/LGFae/swww): Wayland wallpapers tool.
- [rogauracore](https://github.com/wroberts/rogauracore): CLI tool for changing keyboard color on ASUS ROG laptops.
- [rofi](https://github.com/davatorium/rofi): Required for the wallpapers menu.

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
exec-once = python3 ~/your/path/to/auto_walls/src/auto_walls.py

bind = $secondMod, F5,       exec, python3 ~/your/path/to/auto_walls/src/set_next.py
bind = $secondMod SHIFT, F5, exec, python3 ~/your/path/to/auto_walls/src/set_prev.py

bind = $mainMod, Y, exec, python3 ~/your/path/to/auto_walls/src/rofi_selector.py
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
    "notify": true,
    "backlight_transition": false,
    "rofi-theme": ""
}
```

- **"interval"**: Time interval in minutes for changing wallpapers. Set to 0 to disable automatic wallpaper changes.
- **"wallpapers_dir"**: Directory where wallpapers are stored.
- **"wallpapers_cli"**: Command to set wallpaper (`<picture>` is placeholder for wallpaper path). Can be customized; for example, for `feh`, use "feh --bg-fill <picture>".
- **"keyboard_cli"**: Command to change keyboard color (`<color>` is placeholder).
- **"keyboard_transition_cli"**: Command for transitioning keyboard backlight color. Example simulates a breathing effect (`<prev>` represents previous color and `<color>` is new color).
- **"change_backlight"**: Enable/disable keyboard backlight changes.
- **"notify"**: Enable/disable notifications.
- **"backlight_transition"**: Enable/disable backlight transition effects.
- **"rofi-theme"**: Path to a custom Rofi theme when using `rofi_selector.py`; leave empty for default theme..
