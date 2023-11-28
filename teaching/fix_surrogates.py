#!/usr/bin/env python

from pathlib import Path
from typing import Annotated, Optional
import typer

app = typer.Typer()


def fix_win_surrogates(s: str, encoding="cp1252"):
    codepoints = [ord(c) for c in s]
    fixed = [cp & 0xFF if 0xD800 <= cp <= 0xE000 else cp for cp in codepoints if cp > 0]
    encoded = bytes(fixed)
    decoded = encoded.decode(encoding)
    return decoded


@app.command()
def main(
    files: Annotated[Optional[list[str]], typer.Argument()] = None,
    encoding: str = "cp437",
    verbose: bool = False,
):
    """
    There seems to be a bug in some Windows zip software that encodes filenames
    using the Windows codepage instead of either old cp437 or UTF-8. When popular
    unzip libraries unpack such archives in a UTF-8 locale, non-ASCII characters
    may end up as unicode surrogate characters. This script fixes these filenames
    after the fact, i.e. it renames the unpacked files.

    If no files are given, work on all files in the current directory.

    Encoding is the encoding to use to decode the entries. If verbose, all files are reported.
    """
    if files:
        paths = [Path(file) for file in files]
    else:
        paths = list(Path().iterdir())
    for path in paths:
        orig = path.name
        fixed = fix_win_surrogates(path.name, encoding=encoding)
        if orig != fixed:
            print(f"{orig!r} => {fixed}")
            path.rename(path.with_name(fixed))
        elif verbose:
            print(f"Not renaming {orig!r}")
