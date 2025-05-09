from auto_walls import State, get_config, notify
from psutil import Process, pid_exists
from subprocess import Popen

import os

def start_timer(interval: str, do_notify: bool):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    process = Popen([f"{script_dir}/timer", str(interval)])
    state.timer_pid = process.pid

    if do_notify:
        notify(f"Starting timer process with pid: {process.pid}")

def stop_timer(do_notify: bool, pid: int):
    Process(pid).kill()
    state.timer_pid = -1

    if do_notify:
        notify("Ending timer process ..")

if __name__ == '__main__':
    state = State()
    c = get_config()

    try:
        if (state.timer_pid and state.timer_pid != -1) and pid_exists(state.timer_pid) \
            and os.readlink(f'/proc/{state.timer_pid}/cwd') == os.path.dirname(os.path.abspath(__file__)):

            stop_timer(c["notify"], state.timer_pid)
        else:
            start_timer(c["interval"], c["notify"])

    except ValueError:
        start_timer(c["interval"], c["notify"])