#!/usr/bin/env python3
import tempfile
from os import fspath
from pathlib import Path
from subprocess import run

import click

@click.command()
@click.argument('video')
@click.option('-o', '--save-as', help="JPEG or PNG file to save. Default <video>-title.jpg except if embed is true.")
@click.option('-e', '--embed', is_flag=True, help="Try to embed the title frame as a thumbnail")
@click.option('-s', '--seek', help="skip before extracting stuff")
def extract_thumbnail(video, save_as=None, embed=False, seek=None):
    video = Path(video)
    if save_as:
        target = Path(save_as)
    elif embed:
        target = Path(tempfile.TemporaryDirectory().name, video.stem + '-title.jpg')
    else:
        target = video.with_name(video.stem + '-title.jpg')
    args = ['ffmpeg', '-hide_banner']
    if seek:
        args.extend(['-ss', seek])
    args.extend(['-i', fspath(video), '-vframes', '1', '-f', 'image2', fspath(target)])
    run(args)

    if embed:
        run(['AtomicParsley', fspath(video), '--artwork', fspath(target)])


if __name__ == '__main__':
    extract_thumbnail()
