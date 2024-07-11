from auto_walls import StateParser, ConfigParser, reset_state, set_wallpaper
import os


def main(state_dir='~/auto_walls/state.json',
         config_dir='~/.config/auto_walls/config.json'):
    
    while True:
        state  = StateParser(state_dir).parse_state()
        c = ConfigParser(config_dir).parse_config()

        wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])

        if state["index"] == -2: # no state, first run
            reset_state(wallpapers_dir, state_dir)
            continue

        else: #there are wallpapers 
            i = state["index"] + 1
            try:
                current_wallpaper = os.path.join(wallpapers_dir, state["wallpapers"][i])

            except: #index out of range
                reset_state(wallpapers_dir, state_dir)
                continue
            
        set_wallpaper(c["wallpapers_cli"], current_wallpaper, i, state_dir, c["change_backlight"], c["backlight_transition"])
        break

if __name__ == '__main__':
    main()