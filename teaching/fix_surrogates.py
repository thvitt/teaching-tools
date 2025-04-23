#!/usr/bin/env python

from pathlib import Path
from typing import Annotated, Iterable, Optional, overload
import typer
from collections import defaultdict

from rich import print

app = typer.Typer()

UNKKNOWN_CHAR = chr(0xFFFD)


class Uncoder:
    def __init__(self, encoding: str):
        self.encoding = encoding
        encoded_chars = bytes(range(256)).decode(encoding)
        original_src = map(chr, range(256))
        back_map = dict(zip(encoded_chars, original_src))
        self.decode_map = defaultdict(lambda: UNKKNOWN_CHAR)
        self.decode_map.update(back_map)

    def __call__(self, s: str) -> str:
        return "".join(self.decode_map[c] for c in s)


@overload
def fix_win_surrogates(s: str, encoding: str) -> str: ...


@overload
def fix_win_surrogates(s: str, encoding: None) -> bytes: ...


def fix_win_surrogates(
    s: str, encoding: str | None = "cp1252", fix_plus=True
) -> str | bytes:
    codepoints = [ord(c) for c in s]
    fixed = []
    for cp in codepoints:
        if 0xD800 <= cp <= 0xDBFF or 0xDC00 <= cp <= 0xDFFF:  # low or high urrogate
            if fix_plus and fixed and fixed[-1] == ord("+"):
                fixed.pop()
            fixed.append(cp & (0x400 - 1))
        else:
            fixed.append(cp)
    mark = "".join("^" if cp > 255 else " " for cp in fixed)
    if mark.strip():
        adjusted = "".join("?" if 0xD800 <= cp <= 0xD8FF else chr(cp) for cp in fixed)
        raise ValueError(f"Invalid characters in input:\n{adjusted}\n{mark}")
    encoded = bytes(fixed)
    if encoding is None:
        return encoded
    else:
        decoded = encoded.decode(encoding)
        return decoded


def _recursive_list(*roots: Path | str) -> Iterable[Path]:
    for root_ in roots:
        root = Path(root_)
        for path, dirnames, filenames in root.walk(top_down=False):
            for name in dirnames + filenames:
                yield path / name


@app.command()
def main(
    files: Annotated[Optional[list[str]], typer.Argument()] = None,
    encoding: str = "cp437",
    verbose: Annotated[bool, typer.Option("-v", "--verbose")] = False,
    simulate: Annotated[bool, typer.Option("-n", "--dry-run", "--simulate")] = False,
    recursive: Annotated[bool, typer.Option("-r", "--recursive")] = False,
    uncode: Annotated[bool, typer.Option("-u", "--uncode")] = False,
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
        if recursive:
            paths = list(_recursive_list(*files))
        else:
            paths = [Path(file) for file in files]
    elif recursive:
        paths = list(_recursive_list(Path()))
    else:
        paths = list(Path().iterdir())

    for path in paths:
        try:
            orig = path.name
            if uncode:
                fixed = Uncoder(encoding)(orig)
            else:
                fixed = fix_win_surrogates(path.name, encoding=encoding)
            if orig != fixed:
                print(f"{orig!r} => {fixed}")
                if not simulate:
                    path.rename(path.with_name(fixed))
            elif verbose:
                print(f"[dim]Not renaming {orig!r}[/dim]")
        except ValueError as e:
            print(f"{path}: [red]{e}[/red]")
