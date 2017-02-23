#!/usr/bin/env python
import argparse
import os
import sys

from gooey import Gooey, GooeyParser

from nanonet.nanonetcall import main as nanonet_main


def get_gui_parser():
    parser = GooeyParser(description='nanonet basecaller')
    parser.add_argument('input', help='input folder', widget='DirChooser')
    parser.add_argument('output', help='output file', widget='FileChooser')
    parser.add_argument('--chemistry', choices=['R9', 'R9.4'], default='R9.4', help='Sequencing chemistry')
    parser.add_argument('--jobs', type=int, default=1, help='No. CPUs to use')
    return parser


@Gooey
def main():
    args = get_gui_parser().parse_args()
    nanonet_main(args)


if __name__ == "__main__":
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
    main()
