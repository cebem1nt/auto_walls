#!/usr/bin/env python3
import os, json, random
from subprocess import run, Popen
from psutil import pid_exists, Process

def notify(message: str, lvl='normal'):
    run(["notify-send", message, "-a", "wallpaper", "-u", lvl, "-i", "preferences-desktop-wallpaper"])

def get_config(file='~/.config/auto_walls/config.json'): 
    file = os.path.expanduser(file)

    default_config = {  
            "intervall"               : 30,
            "wallpapers_dir"          : "~/Pictures",
            "wallpapers_cli"          : "swww img <picture>",
            "keyboard_cli"            : "rogauracore single_static <color>",
            "keyboard_transition_cli" : "rogauracore single_breathing <prev> <color> 3",
            "transition_duration"     : 1.1,
            "change_backlight"        : False,
            "notify"                  : True,
            "backlight_transition"    : False,
            "rofi_theme"              : ""
        }

    if not os.path.exists(os.path.dirname(file)): 
        # ensuring that the passed dir exist
        os.makedirs(os.path.dirname(file))
        with open(file, 'w') as f:
            return default_config

    with open(file) as f:
        try:
            return json.load(f)
        except:
            with open(file, 'w') as wf:
                json.dump(default_config, wf, indent=4, separators=(', ', ': '))
            
            return default_config

class State:    
    root = os.path.expanduser('~/.local/share/auto_walls')
    _cache = {}

    def __init__(self) -> None:
        self._wallpapers_dir = os.path.join(self.root, 'wallpapers.json')
        self._timer_pid_dir = os.path.join(self.root, 'pid')
        self._index_dir = os.path.join(self.root, 'index')
        self._prev_kb_color_dir = os.path.join(self.root, 'prev_kb')

        if not os.path.exists(self.root):
            os.makedirs(self.root)

    def _read_from_file(self, dir: str):
        if dir in self._cache:
            return self._cache[dir]

        if not os.path.exists(dir):
            return None
        
        with open(dir) as f:
            content = f.read()
            return int(content) if content.isdigit() else content

    def _write_to_file(self, dir: str, value: int | str):
        with open(dir, 'w') as f:
            f.write(str(value))
        self._cache[dir] = value

    @property
    def wallpapers(self) -> list[str]:
        if "wallpapers" in self._cache:
            return self._cache["wallpapers"]

        if not os.path.exists(self._wallpapers_dir):
            return None

        with open(self._wallpapers_dir) as f:
            try:
                wallpapers = json.load(f)
                self._cache["wallpapers"] = wallpapers
                return wallpapers
            except json.JSONDecodeError:
                return None

    @wallpapers.setter
    def wallpapers(self, val: list[str]) -> None:
        with open(self._wallpapers_dir, 'w') as f:
            json.dump(val, f)
        self._cache["wallpapers"] = val 

    @property
    def timer_pid(self):
        return self._read_from_file(self._timer_pid_dir)

    @timer_pid.setter
    def timer_pid(self, val: int):
        self._write_to_file(self._timer_pid_dir, val)

    @property
    def index(self):
        return self._read_from_file(self._index_dir)

    @index.setter
    def index(self, val: int):
        self._write_to_file(self._index_dir, val)

    @property
    def prev_kb_color(self):
        return self._read_from_file(self._prev_kb_color_dir)

    @prev_kb_color.setter
    def prev_kb_color(self, val: str):
        self._write_to_file(self._prev_kb_color_dir, val)

    def reset_state(self, user_wallpapers_dir: str, do_notify=False):
        user_wallpapers_dir = os.path.expanduser(user_wallpapers_dir)
        wallpapers = []

        if not os.path.exists(user_wallpapers_dir):
            raise FileNotFoundError(f"No such a directory: {user_wallpapers_dir} !")

        if do_notify:
            notify("Shuffling wallpapers..")

        for w in os.listdir(user_wallpapers_dir):
            w = os.path.join(user_wallpapers_dir, w) # completed dir for each wallpaper
            if os.path.isfile(w): 
                wallpapers.append(w)

        if not len(wallpapers):
            raise ValueError(f"There are no wallpapers in {user_wallpapers_dir} !")

        random.shuffle(wallpapers)
        self.wallpapers = wallpapers
        self.index = -1

def set_wallpaper(config: dict, state: State, current_wallpaper: str, index: int, do_change_index=True):  
    wallpapers_command = config["wallpapers_cli"] 

    if not os.path.exists(current_wallpaper):
        # wallpaper that we try to set was renamed or deleted
        state.reset_state(config["wallpapers_dir"], config["notify"])

        notify(f"Error, could not find {current_wallpaper}, try running auto_walls.py again", 'critical')

    lock_file = os.path.expanduser('~/.local/share/auto_walls/auto_walls.lock')

    if not os.path.exists(lock_file):
        try:
            open(lock_file, 'w').close()

            cli = wallpapers_command.replace("<picture>", current_wallpaper)
            
            if do_change_index:
                state.index = index
                print(f'changed wallpaper, index : {index}')

            run(cli.split())

            if config["change_backlight"]: 
            # running keyboard module to find the best collor and set it
                from modules.kb_backlight import set_backlight
                set_backlight(state, current_wallpaper, config["backlight_transition"],
                            config["keyboard_cli"], config["keyboard_transition_cli"], config["transition_duration"])
            
        finally:
            os.remove(lock_file)

def main():
    c = get_config()
    state = State()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        if state.timer_pid != -1:
            if pid_exists(state.timer_pid) and os.path.basename(os.readlink(f'/proc/{state.timer_pid}/exe')) == 'timer':
                return
            else:
                state.timer_pid = -1

        process = Popen([os.path.join(script_dir, 'timer'), str(c["intervall"])])
        state.timer_pid = process.pid
        print(f"New timer process started with pid: {process.pid}")
        
    except Exception as e:
        print(f"Error while running: {e}")

if __name__ == '__main__':
    main()