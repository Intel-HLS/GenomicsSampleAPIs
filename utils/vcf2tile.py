"""
  The MIT License (MIT)
  Copyright (c) 2016 Intel Corporation

  Permission is hereby granted, free of charge, to any person obtaining a copy of 
  this software and associated documentation files (the "Software"), to deal in 
  the Software without restriction, including without limitation the rights to 
  use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
  the Software, and to permit persons to whom the Software is furnished to do so, 
  subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all 
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
  FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
  IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

#!/usr/bin/env python

import utils.vcf_importer as multiprocess_import
import utils.helper as helper

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Register VCF with MetaDB and create TileDB JSON.")

    parser.add_argument(
        "-c", 
        "--config", 
        required=True, 
        type=str,
        help="input configuration file for VCF import")

    parser.add_argument(
        "-d",
        "--outputdir", 
        required=True, 
        type=str, 
        help="Output directory where the outputs need to be stored")

    parser.add_argument(
        "-i", 
        "--inputs", 
        nargs='+', 
        type=str,
        required=True, 
        help="VCF files to be imported.")

    parser.add_argument(
        "-a",
        "--append_callsets",
        required=False,
        type=str,
        help="CallSet mapping file to append.")

    parser.add_argument(
        "-l",
        "--loader",
        required=False,
        type=str,
        help="Loader JSON to load data into Tile DB.")

    args = parser.parse_args()

    multiprocess_import.parallelGen(
        args.config, 
        args.inputs, 
        args.outputdir, 
        callset_file=args.append_callsets,
        loader_config=args.loader)
