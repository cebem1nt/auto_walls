#!/usr/bin/env python3
import os, json, random
from subprocess import run, Popen
from psutil import pid_exists, Process

def notify(message: str, lvl='normal'):
    run(["notify-send", message, "-a", "wallpaper", "-u", lvl])

class Parser: 
    # a superior class for files parsing 
    def __init__(self, file: str) -> None:
        self.file = os.path.expanduser(file)

    def parse(self):
        if not os.path.exists(os.path.dirname(self.file)): 
            # ensuring that the passed dir exist
            os.makedirs(os.path.dirname(self.file))
            with open(self.file, 'w') as f:
                pass

        with open(self.file) as f:
            # parsing file's content
            try:
                return json.load(f)
            except:
                return None
            
class ConfigParser(Parser):  
    # a sub class for config parsing
    def __init__(self, file) -> None:
        super().__init__(file)

    def parse_config(self): 
        config = self.parse() 
        # parsing file's content by inherited method

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

class StateParser(Parser):             
    # a sub class for state parsing*
    # we'll store a list of wallpapers directories and index
    # of the current one, to make possible setting next and previous one
    def __init__(self, file) -> None:  
        super().__init__(file)         

    def parse_state(self):
        state = self.parse()

        if not state: # default state
            state = {
                "wallpapers": [],
                "index"     : -2,
                "timer_pid" : -1,
                "prev_color": '' ,
                "cache" : {}
            }

        return state

class State:
    def __init__(self, state_dir='~/.local/share/auto_walls/state.json') -> None:
        self.dir = os.path.expanduser(state_dir)
        self.update_state()

    def update_state(self):
        parsed_state = StateParser(self.dir).parse_state()
        self.parsed_state = parsed_state
        self.timer_pid = parsed_state["timer_pid"]
        self.prev_kb_color: str = parsed_state["prev_color"]
        self.wallpapers: list = parsed_state["wallpapers"]
        self.index: str = parsed_state["index"]
        self.cache: dict = parsed_state["cache"]

    def write_to_state(self, property: str, value: any): 
        # writing any property and value to the state
        self.parsed_state[property] = value                      
        # setting new value to the passed property

        with open(self.dir, 'w') as f:
            json.dump(self.parsed_state, f, indent=4, separators=(', ', ': '))
    
    def reset_state(self, wallpapers_dir: str, do_notify=False):  
        # reseting state in case we dont have one yet ,
        # or if a wallpaper was the last one
        wallpapers_dir = os.path.expanduser(wallpapers_dir)
        wallpapers = []

        if do_notify:
            notify("Shuffling wallpapers..")

        for w in os.listdir(wallpapers_dir):
            if os.path.isfile(os.path.join(wallpapers_dir, w)): 
                w = os.path.join(wallpapers_dir, w) # completed dir for each wallpaper
                wallpapers.append(w)

        if len(wallpapers) == 0: # no wallpapers at all
            if do_notify:
                notify(f"No wallpapers in {wallpapers_dir}", "critical")
                notify("Change the config file!", "critical")

            raise FileNotFoundError(f'No wallpapers found in {wallpapers_dir}')
        
        random.shuffle(wallpapers)

        self.write_to_state("wallpapers", wallpapers)
        self.write_to_state("index", -1)              
        # -1 is to set the first wallpaper, because we assume
        # that state["index"] is the index of the previous wallpaper
        # so index of next one will be previous + 1
        # in this case we will get 0, which is the first wallpaper 
        self.update_state()

def set_wallpaper(config: dict, state: State, current_wallpaper: str, 
                  index: int, do_write_to_state=True):  
    
    # a function to set wallpaper and manage next steps based on the config file
    wallpapers_command = config["wallpapers_cli"] 
    change_backlight = config["change_backlight"]

    if not os.path.exists(current_wallpaper):
        # wallpaper that we try to set was renamed or deleted
        state.reset_state(config["wallpapers_dir"], config["notify"])
        notify(f"Error, could not find {current_wallpaper}, try running auto_walls.py again", 'critical')

    cli = wallpapers_command.replace("<picture>", current_wallpaper)
    run(cli.split())

    if change_backlight: 
    # running keyboard module to find the best collor and set it
        from modules.kb_backlight import set_backlight
        set_backlight(state, current_wallpaper, config["backlight_transition"],
                      config["keyboard_cli"], config["keyboard_transition_cli"], config["transition_duration"])

    if do_write_to_state:
        state.write_to_state("index", index)
        print(f'changed wallpaper, index : {index}')

def main(config_dir = '~/.config/auto_walls/config.json'):
    
    c = ConfigParser(config_dir).parse_config()    # getting config file
    state = State()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        if state.timer_pid != -1:
            if pid_exists(state.timer_pid):
                print(f"auto_walls daemon is already running in backgound with pid {state.timer_pid}")
                restart = input("Restart it ? [Y/n] ")
                if 'y' == restart.lower():
                    Process(state.timer_pid).kill()

                if 'n' == restart.lower():
                    return
            else:
                state.write_to_state("timer_pid", -1)

        process = Popen(f"{script_dir}/timer {c["intervall"]}".split())
        state.write_to_state("timer_pid", process.pid)
        print(f"New timer process started with pid: {process.pid}")
        
    except Exception as e:
        print(f"Error while running: {e}")

    return

if __name__ == '__main__':
    main()