#!/usr/bin/env python3

from auto_walls import get_config, set_wallpaper, State 
from argparse import ArgumentParser

if __name__ == '__main__':
    p = ArgumentParser(description='Set exact wallpaper')

    p.add_argument('wallpaper', type=str, 
                   help='Wallpaper to set')
    
    args = p.parse_args()
    
    set_wallpaper(get_config(), State(), args.wallpaper, -1, do_change_index=False)
