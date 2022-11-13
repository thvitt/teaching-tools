#!/usr/bin/env python3

__version__ = "0.1.0"

from collections import defaultdict
from os import fspath, PathLike
from os.path import relpath
from pathlib import Path
from typing import Dict, List

import click

from lxml import etree


@click.command(help="Move and rename resources used within a MLT file beside the MLT file itself.")
@click.argument("mltfile", type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option("-s", "--sort-by-name", help="count resources by name instead of by position", is_flag=True)
@click.option("-f", "--use-filename", help="include the filename instead of an index in the new name", is_flag=True)
@click.option("-l", "--link", help="don’t move just link", is_flag=True)
@click.option("-b", "--backup", help="create a backup of the target file", is_flag=True)
@click.option("-n", "--dry-run", help="don't do anything, just pretend", is_flag=True)
def move_resources(mltfile: Path, sort_by_name: bool = False, use_filename: bool = False, backup: bool = False,
                   link: bool = False, dry_run: bool = False):
    if not isinstance(mltfile, PathLike):
        mltfile = Path(mltfile)
    source: Path = mltfile.resolve()
    mlt = etree.parse(str(mltfile))

    resource_els = mlt.xpath('//producer/property[@name="resource"]')
    resources: Dict[Path, List[etree.ElementBase]] = defaultdict(list)
    for el in resource_els:
        path = source.parent / el.text
        if path.exists():
            resources[path].append(el)

    order: List[Path] = sorted(resources) if sort_by_name else list(resources)
    for index, resource in enumerate(order, start=1):
        elements = resources[resource]
        fn_pattern = "{mlt}.{stem}{suffix}" if use_filename else "{mlt}.{index:02}{suffix}"
        newloc = source.parent / fn_pattern.format_map(
            dict(mlt=source.stem, stem=resource.stem, index=index, suffix=resource.suffix))
        newrel = Path(relpath(newloc, mltfile.parent))
        click.echo(f"{resource} => {newrel} ({len(elements)} refs)")
        if not dry_run:
            if link:
                newloc.link_to(resource)
            else:
                resource.rename(newloc)
        for element in elements:
            element.text = newrel.as_posix()
            caption = element.getparent().xpath('property[@name="shotcut:caption"]')[0]
            if caption.text == resource.name:
                caption.text = newloc.name

    if not dry_run:
        if backup:
            source.rename(source.with_suffix(source.suffix + '~'))
        mlt.write(fspath(mltfile), pretty_print=True, encoding='utf-8', xml_declaration=True)
    else:
        for el in resource_els:
            etree.dump(el)


if __name__ == '__main__':
    move_resources()
