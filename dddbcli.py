#!/usr/bin/env python3

import argparse
import dddb.video as video
parser = argparse.ArgumentParser(description="DeadDrop DropBox command line utility", prog=__file__)
commandgroup = parser.add_mutually_exclusive_group(required=True)
commandgroup.add_argument("-f", "--fetch", nargs=1,
                    metavar="file_name",
                    help="fetch files")
commandgroup.add_argument("-e", "--encode", nargs=1,
                    metavar="file_name",
                    help="encode the input file")
commandgroup.add_argument("-d", "--decode", nargs=1,
                    metavar="file_name",
                    help="decode the input file")

parser.add_argument("-p", "--protocol", nargs=1,
                    type=str, metavar="protocol_name",
                    choices=["yt", "ytfake"],
                    help="specifies protocol",
                    required=True)


args=parser.parse_args()
