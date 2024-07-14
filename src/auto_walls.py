#!/usr/bin/env python3

import os, json, random, time, subprocess, argparse

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
                      config["keyboard_cli"], config["keyboard_transition_cli"])

    write_to_state("index", index, state_dir)
    print(f'changed wallpaper, index : {index}')

def main(config_dir: str, state_dir: str):
    while True:
        state  = StateParser(state_dir).parse_state()  # getting current state
        c = ConfigParser(config_dir).parse_config()    # getting config file

        wallpapers_dir = os.path.expanduser(c["wallpapers_dir"])

        if state["index"] == -2 : # no state, first run
            reset_state(wallpapers_dir, state_dir, c["notify"])
            continue

        else: # there are wallpapers 
            i = state["index"] + 1
            try:
                current_wallpaper = state["wallpapers"][i]

            except: #index out of range
               reset_state(wallpapers_dir, state_dir, c["notify"])
               continue
        
        set_wallpaper(c, state_dir, current_wallpaper, i)

        if c["intervall"] <= 0: # dont cycle wallpapers, initialize system and say chao
            return

        time.sleep(c["intervall"] * 60)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description="""
                                    A python wallpapers system main script. 
                                    Sets all the system, and changes wallpapers every intervall specified in the config file. 
                                    By default works as background daemon, but will not if intervall is set to 0. 
                                    all additional params can be set in the config file, default location is '~/.config/auto_walls/config.json'. 
                                    Default config file will be generated after first run.
                                    Additional info can be found at https://github.com/cebem1nt/auto_walls
                                """)

    p.add_argument('-c', '--config', 
                   help='Specify the config file', 
                   default='~/.config/auto_walls/config.json')
    
    p.add_argument('-s', '--state', 
                    help='Specify the state file', 
                    default='~/.auto_walls/state.json')

    args = p.parse_args()
    main(state_dir=args.state, config_dir=args.config)