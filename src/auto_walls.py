import os, json, random, time

class Parser:
    def __init__(self, dir) -> None:
        self.dir = os.path.expanduser(dir)

    def ensure_dir_exists(self):
        if not os.path.exists(os.path.dirname(self.dir)):
            os.makedirs(os.path.dirname(self.dir))
            with open(self.dir, 'w') as f:
                pass

    def parse(self):
        self.ensure_dir_exists()
        with open(self.dir) as f:
            try:
                return json.load(f)
            except:
                return None
            
class ConfigParser(Parser):
    def __init__(self, dir) -> None:
        super().__init__(dir)

    def parse_config(self):
        config = self.parse()

        if not config:
            config = {
                "intervall"      : 30,
                "wallpapers_dir" : "~/Pictures",
                "wallpapers_cli" : "swww img <picture>",
                "change_keyboard": False
            }

            with open(self.dir, 'w') as f: # writing default config
                f.write(json.dumps(config))

        return config

class StateParser(Parser):
    def __init__(self, dir) -> None:
        super().__init__(dir)

    def parse_state(self):
        state = self.parse()

        if not state:
            state = {
                "wallpapers": [],
                "index"     : -1
            }

        return state

def _write_to_state(param, value, state_dir: str):
    state_dir = os.path.expanduser(state_dir)

    state = StateParser(state_dir).parse_state()
    state[param] = value

    with open(state_dir, 'w') as f:
        f.write(json.dumps(state))
    
def _reset_state(wallpapers_dir: str, state_dir: str):
    state_dir = os.path.expanduser(state_dir)
    wallpapers = []

    for w in os.listdir(wallpapers_dir):
        if os.path.isfile(os.path.join(wallpapers_dir, w)):
            wallpapers.append(w)

    if len(wallpapers) == 0: # no wallpapers at all
        raise FileNotFoundError(f'There are no wallpapers in {wallpapers_dir}')
    else:
        random.shuffle(wallpapers)
        _write_to_state("wallpapers", wallpapers, state_dir)
        _write_to_state("index", 0, state_dir)

def main(state_dir='~/auto_walls/state.json', 
         config_dir='~/.config/auto_walls/config.json'):

    while True:
        state  = StateParser(state_dir).parse_state()
        config = ConfigParser(config_dir).parse_config()

        wallpapers_dir = os.path.expanduser(config["wallpapers_dir"])

        if len(state["wallpapers"]) == 0: # no state, first run
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
        time.sleep(config["intervall"] * 60)


if __name__ == '__main__':
    main()