from auto_walls import StateParser, ConfigParser, _reset_state, _write_to_state
import os


def main(state_dir='~/auto_walls/state.json',
         config_dir='~/.config/auto_walls/config.json'):
    
    while True:
        state  = StateParser(state_dir).parse_state()
        config = ConfigParser(config_dir).parse_config()

        wallpapers_dir = os.path.expanduser(config["wallpapers_dir"])

        if len(state["wallpapers"]) == 0: # asuming that no state, first run
            _reset_state(wallpapers_dir, state_dir)
            continue

        else: #there are wallpapers 
            i = state["index"] + 1
            try:
                current_wallpaper = os.path.join(wallpapers_dir, state["wallpapers"][i])

            except: #index out of range
                _reset_state(wallpapers_dir, state_dir)
                continue
            
        cli = config["wallpapers_cli"].replace("<picture>", f"'{current_wallpaper}'")
        os.system(cli)
        _write_to_state("index", i, state_dir)
        print(f'changed wallpaper, index : {i}')
        break

if __name__ == '__main__':
    main()