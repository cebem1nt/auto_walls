from auto_walls import State, get_config, notify
from psutil import Process, NoSuchProcess

if __name__ == '__main__':
    state = State()
    do_notify = get_config()["notify"]

    try:
        if state.timer_pid == -1:
            raise NoSuchProcess(-1)
        
        Process(state.timer_pid).kill()
        notify("Timer stopped")

    except NoSuchProcess:
        if do_notify:
            notify("Timer is already stopped")

    except Exception as e:
        if do_notify:
            notify(f"error: {e}")

    finally:
        state.timer_pid = -1