#!/usr/bin/env python3

"""
This tool is intended to convert a 2-up pdf file to a 1-up file, i.e. the input is expected to be
a series of landscape pages with two virtual portrait-formatted columns, the output will be _two_
portrait pages:

   ----------------         ---------   --------
   | 11111  22222 |         | 11111 |  | 22222 |
   | 11111  22222 |    =>   | 11111 |  | 22222 |
   | 11111  22222 |         | 11111 |  | 22222 |
   ----------------         --------   --------

It is possible to preprocess the file first by autorotating it.
"""

import copy, sys
import logging
from argparse import ArgumentParser, FileType
from tempfile import TemporaryFile, NamedTemporaryFile
from typing import IO, BinaryIO

from PyPDF2 import PdfFileWriter, PdfFileReader

def get_argparser():
    parser = ArgumentParser()
    parser.add_argument('input', type=FileType('rb'))
    parser.add_argument('output', type=FileType('wb'))
    parser.add_argument('-r', '--reverse-order', default=False, action='store_true',
                        help='dump upper / right page first')
    return parser


def split_pages(input: BinaryIO, reverseOrder: bool = False) -> PdfFileWriter:
    logger = logging.getLogger(__name__)
    inpdf = PdfFileReader(input)
    output = PdfFileWriter()
    for i, page in enumerate(inpdf.pages):
        page2 = copy.copy(page)
        w, h = page.mediaBox.upperRight
        landscape = w >= h
        rotation = page.get('/Rotate')
        logger.info('Page %d: landscape=%s, rotation=%s', i, landscape, rotation)
        if landscape:
            page.mediaBox.lowerLeft = (0, 0)
            page.mediaBox.upperRight = (w/2, h)
            page2.mediaBox.lowerLeft = (w/2, 0)
            page2.mediaBox.upperRight = (w, h)
        else:
            page.mediaBox.lowerLeft = (0, 0)
            page.mediaBox.upperRight = (w, h/2)
            page2.mediaBox.lowerLeft = (0, h/2)
            page2.mediaBox.upperRight = (w, h)

        if reverseOrder:
            output.addPage(page2)
            output.addPage(page)
        else:
            output.addPage(page)
            output.addPage(page2)

    return output


def main():
    options = get_argparser().parse_args()
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Options: %s", options)
    result = split_pages(options.input, options.reverse_order)
    if options.output:
        result.write(options.output)
    else:
        with open('out.pdf', 'cb') as output:
            result.write(output)

if __name__ == '__main__':
    main()
