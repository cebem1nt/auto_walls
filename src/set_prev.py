from auto_walls import StateParser, ConfigParser, set_wallpaper
import os, subprocess


def main(state_dir='~/auto_walls/state.json',
         config_dir='~/.config/auto_walls/config.json'):

    state  = StateParser(state_dir).parse_state()
    c = ConfigParser(config_dir).parse_config()

    wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])

    if len(state["wallpapers"]) == 0 or state["index"] <= 0 : # there are no wallpapers or
        print("Cant set previous wallpaper!")                 # allready first wallpaper
        print("index: ", state["index"])
        if c["notify"]:
            subprocess.run(["notify-send", "Cant set previous wallpaper!"])
        return

    else: # wallpaper is not the first one
        i = state["index"] - 1  # setting wallpaper that was before 
        current_wallpaper = os.path.join(wallpapers_dir, state["wallpapers"][i])
        set_wallpaper(c["wallpapers_cli"], current_wallpaper, i, state_dir, c["change_backlight"], c["backlight_transition"])


if __name__ == '__main__':
    main()