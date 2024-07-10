import os, json, random, time

class Parser:
    def __init__(self, dir) -> None:
        self.dir = os.path.expanduser(dir)

    def parse(self):
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

        return config

class StateParser(Parser):
    def __init__(self, dir) -> None:
        super().__init__(dir)

    def parse_state(self):
        state = self.parse()

        if not state:
            state = {
                "wallpapers"   : [],
                "index" : -1
            }

        return state

def _write_to_state(param, value, dir):
    state = StateParser(dir).parse_state()
    state[param] = value

    with open(dir, 'w') as f:
        f.write(json.dumps(state))

def main(state_dir='~/auto_walls/state.json', 
         config_dir='~/.config/auto_walls/config.json'):

    while True:
        state  = StateParser(state_dir).parse_state()
        config = ConfigParser(config_dir).parse_config()

        if len(state["wallpapers"]) == 0: # no state, first run
            wallpapers = os.listdir(config["wallpapers_dir"])
            if len(wallpapers) == 0:
                raise FileNotFoundError(f'There are no wallpapers in {config["wallpapers_dir"]}')
            else:
                random.shuffle(wallpapers)
                _write_to_state("wallpapers", wallpapers, state_dir)
                _write_to_state("index", 0, state_dir)

        else: #there are wallpapers 
            i = state["index"]
            try:
                current_wallpaper = os.path.join(config["wallpapers_dir"], state["wallpapers"][i])

            except: #index out of rage
                wallpapers = os.listdir(config["wallpapers_dir"])
                i = 0 
                random.shuffle(wallpapers)
                _write_to_state("wallpapers", wallpapers, state_dir)
                _write_to_state("index", i, state_dir)
                current_wallpaper = wallpapers[i]
            
            cli = config["wallpapers_cli"].replace("<picture>", current_wallpaper)
            os.system(cli)
            time.sleep(config["intervall"] * 60)


if __name__ == '__main__':
    main()