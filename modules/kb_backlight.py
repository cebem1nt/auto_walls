import numpy as np
import subprocess, time
from PIL import Image
from sklearn.cluster import KMeans

from auto_walls import State

def extract_color(image_path, num_colors=1, size=20):
    img = Image.open(image_path).resize((size, size)).convert('RGB')
    pixels = np.array(img).reshape((-1, 3))

    kmeans = KMeans(n_clusters=num_colors, n_init=1, max_iter=50, random_state=42)
    kmeans.fit(pixels)

    return kmeans.cluster_centers_.astype(int)[0]

def rgb_to_hex(rgb):
    r, g, b = rgb
    return f"{r:02X}{g:02X}{b:02X}"


def set_backlight(state: State, picture: str, transition: bool, 
                  keyboard_cli: str, keyboard_transition_cli: str,
                  transition_duration: float):
    
    if picture in state.cache:
        color = state.cache[picture]

    else:
        color = rgb_to_hex(extract_color(picture))
        state.cache[picture] = color

        state.write_to_state('cache', state.cache)

    if transition:
        try:
            prev_color = state.prev_kb_color
        except:
            prev_color = '010101'

        keyboard_transition_cli = keyboard_transition_cli.replace("<prev>", prev_color)
        keyboard_transition_cli = keyboard_transition_cli.replace("<color>", color)

        subprocess.run(keyboard_transition_cli.split())
        time.sleep(transition_duration)

    keyboard_cli = keyboard_cli.replace("<color>", color)
    subprocess.run(keyboard_cli.split())
    
    print("changed backlight color to :", color)
    state.write_to_state("prev_color", color)