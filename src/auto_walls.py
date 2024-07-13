#!/usr/bin/env python3

import os, json, random, time, subprocess

class Parser:
    def __init__(self, dir) -> None:
        self.dir = os.path.expanduser(dir)

    def parse(self):
        if not os.path.exists(os.path.dirname(self.dir)):
            os.makedirs(os.path.dirname(self.dir))
            with open(self.dir, 'w') as f:
                pass

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

        if not config: # generating default config file
            config = {
                "intervall"           : 30,
                "wallpapers_dir"      : "~/Pictures",
                "wallpapers_cli"      : "swww img <picture>",
                "change_backlight"    : False,
                "notify"              : False,
                "backlight_transition": False,
                "rofi-theme"          : ""
            }

            with open(self.dir, 'w') as f: # writing default config
                f.write(json.dumps(config))

        return config

class StateParser(Parser):
    def __init__(self, dir) -> None:
        super().__init__(dir)

    def parse_state(self):
        state = self.parse()

        if not state: # default state
            state = {
                "wallpapers": [],
                "index"     : -2,
            }

        return state

def write_to_state(param: str, value: any, state_dir: str):
    state_dir = os.path.expanduser(state_dir)

    state = StateParser(state_dir).parse_state()
    state[param] = value

    with open(state_dir, 'w') as f:
        f.write(json.dumps(state))
    
def reset_state(wallpapers_dir: str, state_dir: str, notify=False):
    state_dir = os.path.expanduser(state_dir)
    wallpapers = []
        
    if notify:
        subprocess.run(["notify-send", "Shuffling wallpapers.."])

    for w in os.listdir(wallpapers_dir):
        if os.path.isfile(os.path.join(wallpapers_dir, w)):
            w = os.path.join(wallpapers_dir, w) # now they are complete dirs
            wallpapers.append(w)

    if len(wallpapers) == 0: # no wallpapers at all
        raise FileNotFoundError(f'There are no wallpapers in {wallpapers_dir}')
    else:
        random.shuffle(wallpapers)
        write_to_state("wallpapers", wallpapers, state_dir)
        write_to_state("index", -1, state_dir)

def set_wallpaper(wallpapers_command: str, current_wallpaper: str, index: int, 
                  state_dir: str, change_backlight=False, backlight_transition=False):
    
    cli = wallpapers_command.replace("<picture>", f"{current_wallpaper}")
    subprocess.run(cli.split())

    if change_backlight:
        from kb_backlight import set_backlight
        set_backlight(state_dir, current_wallpaper, backlight_transition)


    write_to_state("index", index, state_dir)
    print(f'changed wallpaper, index : {index}')

def main(state_dir='~/.auto_walls/state.json', 
         config_dir='~/.config/auto_walls/config.json'):

    while True:
        state  = StateParser(state_dir).parse_state()
        c = ConfigParser(config_dir).parse_config()

        wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])

        if state["index"] == -2 : # no state, first run
            reset_state(wallpapers_dir, state_dir, c["notify"])
            continue

        else: #there are wallpapers 
            i = state["index"] + 1
            try:
                current_wallpaper = state["wallpapers"][i]

            except: #index out of range
               reset_state(wallpapers_dir, state_dir, c["notify"])
               continue
        
        set_wallpaper(c["wallpapers_cli"], 
                      current_wallpaper, i, state_dir, c["change_backlight"], c["backlight_transition"])

        if c["intervall"] == 0: # dont cycle wallpapers, initialize system and say chao
            return

        time.sleep(c["intervall"] * 60)


if __name__ == '__main__':
    main()