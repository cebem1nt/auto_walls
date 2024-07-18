import numpy as np
import subprocess, time
from PIL import Image
from sklearn.cluster import KMeans

from auto_walls import StateParser, write_to_state

def extract_color(image_path, num_colors=1, size=20):
    img = Image.open(image_path).resize((size, size)).convert('RGB')
    pixels = np.array(img).reshape((-1, 3))

    kmeans = KMeans(n_clusters=num_colors, n_init=1, max_iter=50, random_state=42)
    kmeans.fit(pixels)

    return kmeans.cluster_centers_.astype(int)[0]

def rgb_to_hex(rgb):
    r, g, b = rgb
    return f"{r:02X}{g:02X}{b:02X}"

def set_backlight(state_dir:str, picture: str, transition: bool, 
                  keyboard_cli: str, keyboard_transition_cli: str,
                  transition_duration: float):
    
    color = rgb_to_hex(extract_color(picture))

    if transition:
        state = StateParser(state_dir).parse_state()
        try:
            prev_color = state["prev_color"]
        except:
            prev_color = '000000'

        keyboard_transition_cli = keyboard_transition_cli.replace("<prev>", prev_color)
        keyboard_transition_cli = keyboard_transition_cli.replace("<color>", color)

        subprocess.run(keyboard_transition_cli.split())
        time.sleep(transition_duration)

    keyboard_cli = keyboard_cli.replace("<color>", color)
    subprocess.run(keyboard_cli.split())
    
    print("changed backlight color to :", color)
    write_to_state("prev_color", color, state_dir)