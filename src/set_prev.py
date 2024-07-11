from auto_walls import StateParser, ConfigParser, _write_to_state
import os


def main(state_dir='~/auto_walls/state.json',
         config_dir='~/.config/auto_walls/config.json'):

    state  = StateParser(state_dir).parse_state()
    config = ConfigParser(config_dir).parse_config()

    wallpapers_dir = os.path.expanduser(config["wallpapers_dir"])

    if len(state["wallpapers"]) == 0 or state["index"] <= 0 : # there are no wallpapers or
        print("cant set previous wallpaper!")                 # allready first wallpaper
        print("index: ", state["index"])
        return

    else: # wallpaper is not the first one
        i = state["index"] - 1  # setting wallpaper that was before 
        current_wallpaper = os.path.join(wallpapers_dir, state["wallpapers"][i])
        cli = config["wallpapers_cli"].replace("<picture>", f"'{current_wallpaper}'")

        os.system(cli)
        _write_to_state("index", i, state_dir) # 
        print(f'changed wallpaper, index : {i}')

if __name__ == '__main__':
    main()