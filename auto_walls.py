#!/usr/bin/env python3
import os, json, random, sys, argparse, signal, subprocess
from psutil import pid_exists, Process

def notify(message: str, lvl='normal'):
    subprocess.Popen([
        "notify-send", message, "auto_walls", 
            "-a", sys.argv[0], 
            "-i", "preferences-desktop-wallpaper",
            "-u", lvl, 
    ])

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
            w = os.path.join(user_wallpapers_dir, w) # complete dir for each wallpaper
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

            subprocess.run(cli)

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

def get_wallpaper_thumbnail(
    wallpaper_file: str, 
    wallpaper_name: str, 
    max_size=500, 
    quality=5
):
    cache_dir = os.path.expanduser('~/.cache/auto_walls/thumbnails')
    wallpaper_thumbnail = os.path.join(cache_dir, wallpaper_name)

    os.makedirs(cache_dir, exist_ok=True)

    if os.path.exists(wallpaper_thumbnail):
        return wallpaper_thumbnail

    else:
        subprocess.run([
            "ffmpeg", 
            "-i", wallpaper_file, 
            "-vf", f"scale='if(gt(iw,ih),{max_size},-1)':'if(gt(iw,ih),-1,{max_size})'", 
            "-frames:v", "1", 
            "-q:v", str(quality), 
            wallpaper_thumbnail
        ])

        return wallpaper_thumbnail

def generate_all_thumbnails(aw: AutoWalls):
    for wallpaper_file in aw.wallpapers:
        wallpaper_name = wallpaper_file.split("/")[-1]
        get_wallpaper_thumbnail(wallpaper_file, wallpaper_name)

def daemon():
    aw = AutoWalls()

    try:
        if aw.timer_pid == -1:
            return print("Timer was turned off on purpose")

        if aw.is_timer_running():
            return print("Timer is allready running")

        process = subprocess.Popen([os.path.join(aw.script_dir, 'timer'), str(aw.config["interval"])])
        aw.timer_pid = process.pid
        print(f"New timer process started with pid: {process.pid}")
        
    except Exception as e:
        raise e

def set_exact(aw: AutoWalls, wallpaper: str):
    aw.set_wallpaper(wallpaper, -1, do_change_index=False)

def rofi(aw: AutoWalls, gen_thumbnails: bool):
    if gen_thumbnails:
        generate_all_thumbnails(aw)
        sys.exit(0)

    rofi_theme = aw.config["rofi_theme"] if aw.config["rofi_theme"] else ' '

    if aw.has_new_wallpapers():
        aw.reset_state()

    opts = ""
    prev = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGTERM, signal.SIG_IGN) # Ignore sigterm in this section

    for wallpaper_file in aw.wallpapers:
        wallpaper_name = wallpaper_file.split("/")[-1]
        wallpaper_thumbnail = get_wallpaper_thumbnail(wallpaper_file, wallpaper_name)

        opts += f"{wallpaper_name}\x00icon\x1f{wallpaper_thumbnail}\n"

    signal.signal(signal.SIGTERM, prev)

    rofi_process = subprocess.Popen(
        ["rofi", "-dmenu", "-i", "-selected-row", str(aw.index), "-theme", rofi_theme],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Pass wallpapers with thumbnails to Rofi
    rofi_process.stdin.write(opts)
    selected_option, _ = rofi_process.communicate()
    selected_option = selected_option.strip()

    # Check if a wallpaper was selected
    if selected_option:
        wallpaper = selected_option.split('\x00icon\x1f')[0] # Extract wallpaper path
        selected_wallpaper_dir = os.path.join(aw.wallpapers_dir, wallpaper)
        
        i = aw.wallpapers.index(selected_wallpaper_dir)
        aw.set_wallpaper(selected_wallpaper_dir, i)

def set_next(aw: AutoWalls):
    do_notify = aw.config["notify"]

    i = aw.index + 1

    if i >= len(aw.wallpapers):
        aw.reset_state()
        i = 0

    aw.set_wallpaper(aw.wallpapers[i], i)

def set_prev(aw: AutoWalls):
    if aw.index <= 0: # allready first wallpaper
        aw.reset_state()
        i = len(aw.wallpapers) - 1 # going from the end

    else:
        i = aw.index - 1  # setting wallpaper that was before 

    aw.set_wallpaper(aw.wallpapers[i], i)


def start_timer(aw: AutoWalls):
    process = subprocess.Popen([
        f"{aw.script_dir}/timer", str(aw.config["interval"])
    ])

    aw.timer_pid = process.pid

    if aw.config["notify"]:
        notify(f"Timer started.")

def stop_timer(aw: AutoWalls):
    try:
        parent = Process(aw.timer_pid)

        for child in parent.children(recursive=True):
            child.kill()
        
        parent.kill()
        aw.timer_pid = -1

        if aw.config["notify"]:
            notify("Ending timer...")
            
    except Exception as e:
        if do_notify:
            notify(f"Error stopping timer process: {str(e)}")

def toggle(aw: AutoWalls):
    try:
        if aw.timer_pid and pid_exists(aw.timer_pid):
            stop_timer(aw)
        else:
            start_timer(aw)

    except ValueError:
        start_timer(aw)

def main(args: argparse.Namespace):
    instance = AutoWalls()

    match args.command:
        case "toggle": toggle(instance)
        case "rofi":   rofi(instance, args.gen_thumbnails)
        case "next":   set_next(instance)
        case "prev":   set_prev(instance)
        case "set":    set_exact(instance, args.wallpaper)
        case _:        daemon()

if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description="A multi tool, wallpapers manager for a WM"
    )

    subps = p.add_subparsers(dest="command", help="Available commands")

    rofi_p = subps.add_parser("rofi", help="Pipe current wallpapers to a rofi")
    rofi_p.add_argument      ("--gen-thumbnails",  action="store_true", help="Generate thumbnails only")

    set_p = subps.add_parser("set",  help="Set given wallpaper")
    set_p.add_argument      ("wallpaper",  metavar="WALLPAPER", type=str, help="Wallpaper path")

    next_p   = subps.add_parser("next",   help="Set next wallpaper")
    prev_p   = subps.add_parser("prev",   help="Set previous wallpaper")
    toggle_p = subps.add_parser("toggle", help="Toggle background daemon on/off")

    main(p.parse_args())