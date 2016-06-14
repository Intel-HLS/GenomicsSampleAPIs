#!/usr/bin/env python

import subprocess
import utils.maf_importer as multiprocess_import
import utils.helper as helper
import utils.loader as loader

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Convert  MAF format to Tile DB CSV")

    parser.add_argument("-c", "--config", required=True, type=str,
                        help="input configuration file for MAF conversion")
    parser.add_argument("-o", "--output", required=True, type=str,
                        help="output Tile DB CSV file (without the path) which will be stored in the output directory")
    parser.add_argument("-d", "--outputdir", required=True, type=str,
                        help="Output directory where the outputs need to be stored")
    parser.add_argument("-i", "--inputs", nargs='+', type=str, required=True,
                        help="List of input MAF files to convert")
    parser.add_argument("-z", "--gzipped", action="store_true", required=False,
                        help="True/False indicating if the input file is a gzipped file or not")
    parser.add_argument(
        "-s", "--spark", action="store_true", help="Run as spark.")
    parser.add_argument('-l', "--loader", required=False, type=str,
                        help="Loader JSON to load data into Tile DB.")

    args = parser.parse_args()

    if args.spark:
        # call spark from within import script
        spark_cmd = ["spark-submit", "maf_pyspark.py", "-c",
                     args.config, "-d", args.outputdir, "-o", args.output, "-i"]
        spark_cmd.extend(args.inputs)
        if subprocess.call(spark_cmd) != 0:
            raise Exception("Error running converter")
    else:
        multiprocess_import.parallelGen(
            args.config, args.inputs, args.outputdir, args.output, args.gzipped)

    if args.loader:
        with open(args.config) as conf:
            conf_json = json.load(conf)
            workspace = conf_json['TileDBSchema']['workspace']
            array = conf_json['TileDBSchema']['array']
        baseFileName = helper.getFileName(args.output)
        callset_mapping_file = "{0}/{1}.callset_mapping".format(
            args.outputdir, baseFileName)
        vid_mapping_file = "{0}/{1}.vid_mapping".format(
            args.outputdir, baseFileName)
        loader.load2Tile(args.loader, callset_mapping_file,
                         vid_mapping_file, workspace, array)
