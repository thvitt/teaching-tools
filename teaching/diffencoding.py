#!/usr/bin/env python3

import codecs
from typing import List, Tuple
from unicodedata import name as _name
import click

def format_ch(char, spec='35.35s'):
    if not char or char == '�':
        return '� ' + format('N/A', spec)
    try:
        return char + ' ' + format(_name(char), spec)
    except ValueError:
        return char + ' ' + format('–', spec)


def get_chars(*, codepoints: range = range(256), encoding: str = 'unicode'):
    if encoding == 'unicode':
        return ''.join(chr(n) for n in codepoints)
    else:
        octet_stream = bytes(codepoints)
        return codecs.decode(octet_stream, encoding=encoding, errors='replace')


def diff_encoding(first: str, second: str) -> List[Tuple[int, str, str]]:
    return [(index, first, second)
            for (index, (first, second)) in enumerate(zip(get_chars(encoding=first), get_chars(encoding=second)))
            if first != second]


@click.command()
@click.argument("first")
@click.argument("second")
def report_diff(first: str, second: str):
    diff = diff_encoding(first, second)
    print(f"Idx   {first:^37}    {second:^37}\n" + \
          "---   --------------------------------    --------------------------------\n" + \
          "\n".join(f"{index:>3d}   {format_ch(left)}    {format_ch(right)}"
                    for index, left, right in diff))


if __name__ == '__main__':
    print(report_diff())
