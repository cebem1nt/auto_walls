#!/usr/bin/env python3

from auto_walls import ConfigParser, set_wallpaper
from argparse import ArgumentParser
import os

def main(wallpaper_dir: str,
         state_dir='~/.auto_walls/state.json', 
         config_dir='~/.config/auto_walls/config.json'):

    c = ConfigParser(config_dir).parse_config()
    set_wallpaper(c, state_dir, wallpaper_dir, -1, do_write_to_state=False)


if __name__ == '__main__':
    p = ArgumentParser(description='Set exact wallpaper')

    p.add_argument('wallpaper', type=str, 
                   help='Wallpaper to set')
    
    args = p.parse_args()
    
    main(os.path.expanduser(args.wallpaper))