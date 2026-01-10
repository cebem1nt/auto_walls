import numpy as np
import subprocess, time, os
from PIL import Image
from sklearn.cluster import KMeans

from auto_walls import AutoWalls

def extract_color(image_path, num_colors=1, size=20):
    img = Image.open(image_path).resize((size, size)).convert('RGB')
    pixels = np.array(img).reshape((-1, 3))

    kmeans = KMeans(n_clusters=num_colors, n_init=1, max_iter=50, random_state=42)
    kmeans.fit(pixels)

    return kmeans.cluster_centers_.astype(int)[0]

def rgb_to_hex(rgb):
    r, g, b = rgb
    return f"{r:02X}{g:02X}{b:02X}"

def _in_cache(key: str, cache_dir: str):
    cache_key = key.replace('/', '^^|%')

    if not os.path.exists(cache_dir):
        return os.makedirs(cache_dir)
    
    if cache_key in os.listdir(cache_dir):
        with open(os.path.join(cache_dir, cache_key)) as f:
            return f.read()
    return None

def _to_cache(key: str, val: str, cache_dir: str):
    cache_key = key.replace('/', '^^|%')

    with open(os.path.join(cache_dir, cache_key), 'w') as f:
        f.write(val)

def set_backlight(aw: AutoWalls, picture: str, transition: bool, keyboard_cli: str, keyboard_transition_cli: str, transition_duration: float | int):
    cache_dir = os.path.expanduser('~/.cache/auto_walls/kb_colors')
    color = _in_cache(picture, cache_dir)

    if color is None:
        print('Calculating...')
        color = rgb_to_hex(extract_color(picture))
        _to_cache(picture, color, cache_dir)

    if transition:
        prev_color = aw.prev_kb_color if aw.prev_kb_color else '010101'

        keyboard_transition_cli = keyboard_transition_cli.replace("<prev>", str(prev_color))
        keyboard_transition_cli = keyboard_transition_cli.replace("<color>", color)

        subprocess.run(keyboard_transition_cli.split())
        time.sleep(transition_duration)

    keyboard_cli = keyboard_cli.replace("<color>", color)
    subprocess.run(keyboard_cli.split())
    
    print("changed backlight color to :", color)
    aw.prev_kb_color = color