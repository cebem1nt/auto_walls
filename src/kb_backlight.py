import numpy as np
import os
from PIL import Image
from sklearn.cluster import KMeans

def extract_color_palette(image_path, num_colors=5, max_size=10):
    img = Image.open(image_path).resize((max_size, max_size)).convert('RGB')
    pixels = np.array(img).reshape((-1, 3))

    # Apply K-means clustering with optimized parameters
    kmeans = KMeans(n_clusters=num_colors, n_init=1, max_iter=50, random_state=42)
    kmeans.fit(pixels)

    return kmeans.cluster_centers_.astype(int)

def rgb_to_hex(rgb):
    r, g, b = rgb
    return f"{r:02X}{g:02X}{b:02X}"


def best_color(colors):
    max_score = -1
    max_color = None
    
    for color in colors:
        r, g, b = color
        score = r + g + b
        
        if score > max_score:
            max_score = score
            max_color = color
            
    return rgb_to_hex(max_color)

def set_backlight(picture: str):
    color = best_color(extract_color_palette(picture))
    print(color)
    os.system(f'rogauracore single_static {color}')