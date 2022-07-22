#!/usr/bin/env python3

import sys
import json
from lxml import etree

def pos2timestr(pos, framerate=30):
    seconds, frames = divmod(pos, framerate)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f'{hours}:{minutes:02}:{seconds:02}'
    else:
        return f'{minutes:02}:{seconds:02}'

def main(filename=None):
    if filename is None:
        filename = sys.argv[1]
    tree = etree.parse(filename)
    framerate = int(tree.xpath('//profile/@frame_rate_num')[0])
    guides_str = tree.xpath('//property[@name="kdenlive:docproperties.guides"]/text()')[0]
    guides = json.loads(guides_str)
    print('Type', 'Time', 'Comment', sep='\t')
    for guide in guides:
        print(guide.get('type'), pos2timestr(guide['pos'], framerate), guide.get('comment'), sep='\t')

if __name__ == '__main__':
    main()
