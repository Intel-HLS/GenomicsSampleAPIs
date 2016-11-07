#!/usr/bin/env python
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


import subprocess
import utils.maf_importer as multiprocess_import
import utils.helper as helper

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Convert  MAF format to Tile DB CSV")

    parser.add_argument(
        "-c", 
        "--config", 
        required=True, 
        type=str,
        help="input configuration file for MAF conversion")
    
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
        help="List of input MAF files to convert")

    parser.add_argument(
        "-z",
        "--gzipped",
        action="store_true",
        required=False,
        help="True/False indicating if the input file is a gzipped file or not")

    parser.add_argument(
        "-s",
        "--spark",
        type=str,
        help="Run as spark. Pass local[*] to run spark locally or the spark master URI")

    parser.add_argument(
        "-o",
        "--output",
        required=False,
        type=str,
        help="output Tile DB CSV file (without the path) which will be stored in the output directory. Required for spark.")

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
    parser.add_argument('-r', '--reference_fasta', required=True, type=str,
                        help='reference fasta file to get the reference Allele information')

    args = parser.parse_args()
    helper.verifyFasta(args.reference_fasta)

    if args.spark:
        # call spark from within import script

        spark_cmd = [
            "spark-submit",
            "--master",
            args.spark,
            "maf_pyspark.py", 
            "-c", args.config, 
            "-d", args.outputdir, 
            "-o", args.output,
            "-r", args.reference_fasta, 
            "-i"]

        spark_cmd.extend(args.inputs)
        if args.loader:
            spark_cmd.extend(['-l', args.loader])
        if args.append_callsets:
            spark_cmd.extend(['-a', args.append_callsets])
        print spark_cmd
        pipe = subprocess.Popen(
            spark_cmd, stderr=subprocess.PIPE)
        output, error = pipe.communicate()

        if pipe.returncode != 0:
            raise Exception("Error running converter\n\nERROR: \n{}".format(error))

    else:
        multiprocess_import.REFERENCE_FASTA = args.reference_fasta
        multiprocess_import.parallelGen(
            args.config,
            args.inputs,
            args.outputdir,
            args.gzipped,
            callset_file=args.append_callsets,
            loader_config=args.loader)
