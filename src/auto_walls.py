#!/usr/bin/env python3

import os, json, random, subprocess, sys

class Parser: # a superior class for files parsing 
    def __init__(self, file) -> None:
        self.file = os.path.expanduser(file)

    def parse(self):

        if not os.path.exists(os.path.dirname(self.file)): # ensuring that the passed dir exist
            os.makedirs(os.path.dirname(self.file))
            with open(self.file, 'w') as f:
                pass

        with open(self.file) as f: # parsing file's content
            try:
                return json.load(f)
            except:
                return None
            
class ConfigParser(Parser):  # a sub class for config parsing
    def __init__(self, file) -> None:
        super().__init__(file)

    def parse_config(self): 
        config = self.parse() # parsing file's content by inherited method

        if not config: 
            # generating default config file and writing it
            config = {  
                "intervall"               : 30,
                "wallpapers_dir"          : "~/Pictures",
                "wallpapers_cli"          : "swww img <picture>",
                "keyboard_cli"            : "rogauracore single_static <color>",
                "keyboard_transition_cli" : "rogauracore single_breathing <prev> <color> 3",
                "transition_duration"     : 1.1,
                "change_backlight"        : False,
                "notify"                  : True,
                "backlight_transition"    : False,
                "rofi-theme"              : ""
            }

            with open(self.file, 'w') as f:
                json.dump(config, f, indent=4, separators=(', ', ': '))

        return config

class StateParser(Parser):             # a sub class for state parsing*
    def __init__(self, file) -> None:  # we'll store a list of wallpapers directories and index
        super().__init__(file)         # of the current one, to make possible setting next and previous one

    def parse_state(self):
        state = self.parse()

        if not state: # default state
            state = {
                "wallpapers": [],
                "index"     : -2,
            }

        return state

def write_to_state(property: str, value: any, state_dir: str): # writing any property and value to the state
    state_dir = os.path.expanduser(state_dir)

    state = StateParser(state_dir).parse_state() # fetching current state
    state[property] = value                      # setting new value to the passed property

    with open(state_dir, 'w') as f:
        f.write(json.dumps(state))
    
def reset_state(wallpapers_dir: str, state_dir: str, notify=False):  # reseting state in case we dont have one yet ,
    state_dir = os.path.expanduser(state_dir)                        # or if a wallpaper was the last one
    wallpapers = []

    for w in os.listdir(wallpapers_dir):
        if os.path.isfile(os.path.join(wallpapers_dir, w)): # making sure that it is not a directory
            w = os.path.join(wallpapers_dir, w) # completed dirs
            wallpapers.append(w)

    if len(wallpapers) == 0: # no wallpapers at all
        if notify:
            subprocess.run(["notify-send", f"No wallpapers in {wallpapers_dir}", "-a", "wallpaper", "-u", "critical"])
            subprocess.run(["notify-send", 'Change config file!', "-a", "wallpaper"])
        raise FileNotFoundError(f'There are no wallpapers in {wallpapers_dir}')
    else:
        random.shuffle(wallpapers)

        if notify:
            subprocess.run(["notify-send", "Shuffling wallpapers..", "-a", "wallpaper"])

        write_to_state("wallpapers", wallpapers, state_dir)
        write_to_state("index", -1, state_dir)              
        # -1 is to set the first wallpaper, because we assume
        # that state["index"] is the index of the previous wallpaper
        # so index of next one will be previous + 1
        # in this case we will get 0, which is the first wallpaper 

def set_wallpaper(config: dict, state_dir, current_wallpaper: str, index: int):  # a function to set wallpaper and manage 
    wallpapers_command = config["wallpapers_cli"]                                # next steps based on the config file
    change_backlight = config["change_backlight"]
    backlight_transition = config["backlight_transition"]

    cli = wallpapers_command.replace("<picture>", f"{current_wallpaper}")
    subprocess.run(cli.split())

    if change_backlight: # running keyboard module to find the best collor and set it
        from kb_backlight import set_backlight
        set_backlight(state_dir, current_wallpaper, backlight_transition,
                      config["keyboard_cli"], config["keyboard_transition_cli"], config["transition_duration"])

    write_to_state("index", index, state_dir)
    print(f'changed wallpaper, index : {index}')

def main(config_dir = '~/.config/auto_walls/config.json'):
    c = ConfigParser(config_dir).parse_config()    # getting config file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        subprocess.Popen(f"python3 {current_dir}/timer.py {c["intervall"]}".split())
    except Exception as e:
        print(f"Error while running the script: {e}")
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()