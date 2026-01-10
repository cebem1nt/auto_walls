from auto_walls import State, get_config, notify
from psutil import Process, pid_exists
from subprocess import Popen

import os

def start_timer(interval: str, do_notify: bool):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    process = Popen([f"{script_dir}/timer", str(interval)])
    state.timer_pid = process.pid

    if do_notify:
        notify(f"Timer started.")

def stop_timer(do_notify: bool, pid: int):
    try:
        parent = Process(pid)

        for child in parent.children(recursive=True):
            child.kill()
        
        parent.kill()
        state.timer_pid = -1

        if do_notify:
            notify("Ending timer...")
            
    except Exception as e:
        if do_notify:
            notify(f"Error stopping timer process: {str(e)}")

if __name__ == '__main__':
    state = State()
    c = get_config()

    try:
        if state.timer_pid and pid_exists(state.timer_pid):
            stop_timer(c["notify"], state.timer_pid)
        else:
            start_timer(c["interval"], c["notify"])

    except ValueError:
        start_timer(c["interval"], c["notify"])