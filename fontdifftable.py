#!/usr/bin/python3

import argparse
import pathlib
import subprocess

def read_font_table(file: str) -> dict[int, str]:
    otfinfo = subprocess.run(['otfinfo', '-u', file], capture_output=True, encoding='utf-8')
    table = {}
    for line in otfinfo.stdout.split('\n'):
        parts = line.split()
        if parts:
            table[int(parts[0][3:], base=16)] = parts[-1]
    return table

def getargparser():
    p = argparse.ArgumentParser(description='Compare fonts for unicode coverage using otfinfo')
    p.add_argument('fontA', help="One of the fonts to compare")
    p.add_argument('fontB', help="The other font to compare")
    #    p.add_argument('-a', '--extra-chars-a', action='store_true', help='Show characters A has over B')
    #    p.add_argument('-b', '--extra-chars-b', action='store_true', help='Show characters B has over A')
    p.add_argument('-h', '--html', nargs=1, help='Output to HTML file')
    return p

