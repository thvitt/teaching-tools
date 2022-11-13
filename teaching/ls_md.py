#!/usr/bin/env python3

import sys
from pathlib import Path
import re
from warnings import warn

from ruamel.yaml import YAML
yaml = YAML()


def first_md_block(path: Path):
    try:
        with path.open() as infile:
            return next(yaml.load_all(infile))
    except Exception as e:
        warn(f'{e} parsing {path}', source=e)

def ls(path: Path):
    if path.is_dir():
        for entry in path.glob('*.md'):
            ls(entry)
    else:
        md = first_md_block(path)
        try:
            title = md['title']
        except:
            title = re.sub(r'[-_]+', ' ', path.stem)
        print(f'* [{title}]({path.with_suffix(".pdf")!s})')

def main(args=sys.argv):
    if len(args) > 1:
        for arg in args[1:]:
            ls(Path(arg))
    else:
        ls(Path())

if __name__ == '__main__':
    main()
