import argparse, time, subprocess, os

def timer(secs):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        if secs == 0:
            return
        subprocess.run(f"python3 {current_dir}/set_next.py".split())
        time.sleep(secs*60)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('time', type=int)
    a = p.parse_args()
    timer(a.time)