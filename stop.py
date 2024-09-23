from auto_walls import State, ConfigParser, notify
from psutil import Process, NoSuchProcess

if __name__ == '__main__':
    state = State()
    do_notify = ConfigParser().parse_config()["notify"]

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
        state.write_to_state("timer_pid", -1)