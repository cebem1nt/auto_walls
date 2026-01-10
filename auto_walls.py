#!/usr/bin/env python3
import os, json, random, sys
from subprocess import run, Popen
from psutil import pid_exists, Process

def notify(message: str, lvl='normal'):
    Popen(["notify-send", message, "auto_walls", "-a", "wallpaper", "-u", lvl, "-i", "preferences-desktop-wallpaper"])

def expand_path(path: str):
    return os.path.expandvars(os.path.expanduser(path))

def get_config(file='~/.config/auto_walls/config.json'): 
    file = os.path.expanduser(file)
    os.makedirs(os.path.dirname(file), exist_ok=True)

    default_config = {  
            "interval"                : 30,
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

    try:
        with open(file) as f:
            return json.load(f)
    
    except:
        with open(file, 'w') as wf:
            json.dump(default_config, wf, indent=4, separators=(', ', ': '))
            return default_config

class State:    
    root = os.path.expanduser('~/.local/share/auto_walls')
    cache = {}

    def __init__(self):
        self._wallpapers_dir = os.path.join(self.root, 'wallpapers.json')
        self._timer_pid_dir = os.path.join(self.root, 'pid.lock')
        self._index_dir = os.path.join(self.root, 'index')
        self._prev_kb_color_dir = os.path.join(self.root, 'prev_kb')

        if not os.path.exists(self.root):
            os.makedirs(self.root)

    def read(self, dir: str):
        if dir in self.cache:
            return self.cache[dir]

        if not os.path.exists(dir):
            return None
        
        with open(dir) as f:
            content = f.read()
            try:
                value = int(content)
            except:
                value = content

        self.cache[dir] = value
        return value

    def write(self, dir: str, value: int | str):
        with open(dir, 'w') as f:
            f.write(str(value))
        self.cache[dir] = value

    @property
    def wallpapers(self) -> list[str]:
        if "wallpapers" in self.cache:
            return self.cache["wallpapers"]

        try:
            with open(self._wallpapers_dir) as f:
                wallpapers = json.load(f)
                self.cache["wallpapers"] = wallpapers
                return wallpapers

        except Exception:
            return None

    @wallpapers.setter
    def wallpapers(self, val: list[str]) -> None:
        with open(self._wallpapers_dir, 'w') as f:
            json.dump(val, f)
        self.cache["wallpapers"] = val 

    @property
    def timer_pid(self):
        return self.read(self._timer_pid_dir)

    @timer_pid.setter
    def timer_pid(self, val: int):
        self.write(self._timer_pid_dir, val)

    @property
    def index(self):
        return self.read(self._index_dir)

    @index.setter
    def index(self, val: int):
        self.write(self._index_dir, val)

    @property
    def prev_kb_color(self):
        return self.read(self._prev_kb_color_dir)

    @prev_kb_color.setter
    def prev_kb_color(self, val: str):
        self.write(self._prev_kb_color_dir, val)

    def _reset_state(self, user_wallpapers_dir: str, do_notify=False):
        user_wallpapers_dir = expand_path(user_wallpapers_dir)
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

class AutoWalls(State):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.wallpapers_dir = expand_path(self.config["wallpapers_dir"])
        
        if not self.wallpapers:
            self.reset_state()

    def set_wallpaper(self, wallpaper: str, index: int, do_change_index=True):  
        wallpapers_command = self.config["wallpapers_cli"] 
        wallpaper = expand_path(wallpaper)

        if not os.path.exists(wallpaper):
            self.reset_state()

        lock_file = os.path.expanduser('~/.local/share/auto_walls/auto_walls.lock')

        if os.path.exists(lock_file):
            with open(lock_file) as f:
                pid = int(f.read())

            if pid_exists(pid):
                sys.exit(0)
            else:
                os.remove(lock_file)

        try:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))

            cli: list[str] = wallpapers_command.split()
            
            for i, cli_part in enumerate(cli):
                if cli_part == "<picture>":
                    cli[i] = wallpaper

            if do_change_index:
                self.index = index
                print(f'changed wallpaper, index : {index}')

            run(cli)

            if self.config["change_backlight"]: 
                from modules.kb_backlight import set_backlight

                set_backlight(self, wallpaper, 
                    self.config["backlight_transition"], self.config["keyboard_cli"], self.config["keyboard_transition_cli"], self.config["transition_duration"])

        finally:
            os.remove(lock_file)

    def is_timer_running(self):
        if not self.timer_pid or self.timer_pid == -1:
            return False 

        if pid_exists(self.timer_pid):
            with open(f"/proc/{self.timer_pid}/cmdline") as f:
                content = f.read()

                if "auto_walls" in content or "timer" in content:
                    return True 

        return False

    def has_new_wallpapers(self):
        return sum(1 for entry in os.scandir(self.wallpapers_dir) if entry.is_file()) != len(self.wallpapers)

    def reset_state(self):
        self._reset_state(self.wallpapers_dir, self.config["notify"])

def main():
    aw = AutoWalls()

    try:
        if aw.timer_pid == -1:
            return print("Timer was turned off on purpose")

        if aw.is_timer_running():
            return print("Timer is allready running")

        process = Popen([os.path.join(aw.script_dir, 'timer'), str(aw.config["interval"])])
        aw.timer_pid = process.pid
        print(f"New timer process started with pid: {process.pid}")
        
    except Exception as e:
        raise e

if __name__ == '__main__':
    main()
