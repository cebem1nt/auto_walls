from auto_walls import State, get_config, notify
from psutil import Process, pid_exists
import os
from subprocess import Popen

if __name__ == '__main__':
    state = State()
    c = get_config()
    script_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        if not state.timer_pid or (state.timer_pid == -1) or not pid_exists(state.timer_pid):
            process = Popen(f"{script_dir}/timer {c["intervall"]}".split())
            state.timer_pid = process.pid
            if c["notify"]:
                notify(f"Continuing timer process with pid: {process.pid}")
        else:
            notify("Already running")
        
    except Exception as e:
        if c["notify"]:
            notify(f"Error while running: {e}")
