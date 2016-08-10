#!/usr/bin/env python

import utils.vcf_importer as multiprocess_import
import utils.helper as helper
import utils.loader as loader

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
