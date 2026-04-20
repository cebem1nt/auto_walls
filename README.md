# Auto walls

## What the hell is this?

**Some day 2 years ago**:

> Hmmmm, I need a script, that would ***set random wallpaper once in N minutes***, 
> but also, I might ***set previous wallpaper or the next one**, And I might
> ***pipe the currentlist of wallpapers into rofi to pick the specific one if I want***. 
> And the icing on the cake - ***It should detect the dominant color of the wallpaper*** 
> ***and set it as backlight color for my keyboard with a fancy transition. ***  

Familiar? Probably not, but if so, this is my solution for a problem

## Requirements

If you will use the color detection, install these python libraries:

### pip
```bash
pip install numpy Pillow scikit-learn
```

### Arch Linux
```bash
sudo pacman -S python-numpy python-scikit-learn python-pillow
```

## Configuration
Firstly after the installation, run `auto_walls.py` from the terminal. The following config will be generated at `~/.config/auto_walls/config.json`:

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
- **"rofi-theme"**: Path to a custom Rofi theme when using `auto_walls.py rofi`; leave empty for default theme.

## Usage

You can run `auto_walls.py` on startup according to your window manager configuration. This will execute the daemon that switches wallpapers once at the interval set in config file. Use `auto_walls.py rofi` to pipe the current wallpapers list into the rofi theme set in config file. `auto_walls.py next` sets next wallpaper, `auto_walls.py prev` sets previous wallpaper.

### Example on Hyprland:

```ini
exec-once = python3 ~/your/path/to/auto_walls/auto_walls.py

bind = ALT, F5,       exec, python3  ~/your/path/to/auto_walls/auto_walls.py next
bind = ALT SHIFT, F5, exec, python3  ~/your/path/to/auto_walls/auto_walls.py prev

bind = SUPER, Y, exec, python3 ~/your/path/to/auto_walls/auto_walls.py rofi
```

```
usage: auto_walls.py [-h] {rofi,set,next,prev,toggle} ...

Multi tool and a wallpapers manager for a WM

positional arguments:
  {rofi,set,next,prev,toggle}
                        Available commands
    rofi                Pipe current wallpapers to a rofi
    set                 Set given wallpaper
    next                Set next wallpaper
    prev                Set previous wallpaper
    toggle              Toggle background daemon on/off

options:
  -h, --help            show this help message and exit
```