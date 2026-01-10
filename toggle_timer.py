from auto_walls import AutoWalls, notify
from psutil import Process, pid_exists
from subprocess import Popen

import os

def start_timer(aw: AutoWalls):
    process = Popen([f"{aw.script_dir}/timer", str(aw.config["interval"])])
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

if __name__ == '__main__':
    aw = AutoWalls()

    try:
        if aw.timer_pid and pid_exists(aw.timer_pid):
            stop_timer(aw)
        else:
            start_timer(aw)

    except ValueError:
        start_timer(aw)