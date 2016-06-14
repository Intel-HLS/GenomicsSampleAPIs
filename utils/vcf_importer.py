# vcf importer

import sys
import os
import uuid
import json
import traceback
from multiprocessing import Pool

from collections import OrderedDict

import vcf
import pysam
from pysam import bcftools

from metadb.api import DBImport
from metadb.models import CallSetToDBArrayAssociation

import utils.helper as helper
import utils.configuration as utils


class VCF:

    def __init__(self, filename, config):
        """
        init uses reads in the vcf
        """
        self.filename = filename
        self.configfile = config

        # TileDB loader specific
        self.callset_mapping = dict()

    def __enter__(self):

        self.file = open(self.filename, 'rb')
        self.reader = vcf.Reader(self.file)

        self.config = open(self.configfile, 'r')

        conf = json.load(self.config)
        self.dburi = conf['dburi']
        self.workspace = conf['workspace']
        # default TN columns normal first column, target second column
        # this can be used for idx in file
        self.source_idx = conf.get('source_idx', 0)
        self.target_idx = conf.get('target_idx', 1)
        # callset map will say how to retrieve the callset names
        # from the vcf metadata, assuming standard two column TN vcf
        self.callset_map = conf.get('callset_loc', None)
        self.array, self.variantset, self.referenceset = helper.registerWithMetadb(
            conf, references=self.reader.contigs)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.close()
        self.config.close()

    def toCallSetDict(self):
        # if the callset_map is not specified, we assume the sample headers
        # are the main identifier for the callset
        # use ordered dict for future expansion to multisample TN vcf
        callsets = OrderedDict()

        # assumption that import files will be single sample TN pair VCFs
        # defaulted to NORMAL TUMOUR column order in the VCF, unless otherwise
        # stated
        if self.callset_map is None:
            if len(self.reader.samples) != 2:
                raise ValueError(
                    "Currently only single TN vcf format supported.")
            elif 'NORMAL' in self.reader.samples:
                raise ValueError("Set callset_loc in import config.")
            else:
                callsets[self.reader.samples[
                    self.source_idx]] = self.reader.samples
                callsets[self.reader.samples[
                    self.target_idx]] = self.reader.samples

        else:
            # if not then, callset names are retrieved from VCF SAMPLE tag
            if len(self.reader.metadata['SAMPLE']) != 2:
                raise ValueError(
                    "Currently only single TN vcf format supported.")
            else:
                source = self.reader.metadata['SAMPLE'][
                    self.source_idx]['SampleName']
                target = self.reader.metadata['SAMPLE'][
                    self.target_idx]['SampleName']
                callsets[source] = [source, target]
                callsets[target] = [source, target]

        return callsets

    def setCallSets(self):

        # get variant set id, register parent models
        callsets = self.toCallSetDict()

        with DBImport(self.dburi).getSession() as metadb:
            for callset in callsets:

                # source and target names
                source = callsets[callset][self.source_idx]
                target = callsets[callset][self.target_idx]

                if callset == source:
                    file_idx = self.source_idx
                else:
                    file_idx = self.target_idx

                # register individual and samples
                indv = metadb.registerIndividual(
                    str(uuid.uuid4()), source + "_" + target)
                src = metadb.registerSample(
                    str(uuid.uuid4()), indv.guid, name=source, info={'type': 'source'})
                trg = metadb.registerSample(
                    str(uuid.uuid4()), indv.guid, name=target, info={'type': 'target'})

                # register callset
                cs = metadb.registerCallSet(str(uuid.uuid4()), src.guid, trg.guid, self.workspace, self.array.name, [
                                            self.variantset.id], name=callset)
                tr = metadb.session.query(CallSetToDBArrayAssociation).filter(
                    CallSetToDBArrayAssociation.callset_id == cs.id).first()

                # temp fill in for capturing genomics db import information
                self.callset_mapping[cs.guid] = {
                    'row_idx': tr.tile_row_id, 'idx_in_file': file_idx, 'filename': self.filename}


def sortAndIndex(inFile, outdir):
    """
    sort and index vcfs to ensure bgzipped, sorted, and indexed
    """
    splitFile = os.path.basename(inFile).split(".")

    if splitFile[-1] == 'vcf':
        #.vcf
        file_name = ".".join(splitFile[:-1])
    elif splitFile[-2] == 'vcf' and splitFile[-1] == 'gz':
        # .vcf.gz
        file_name = ".".join(splitFile[:-2])
    else:
        raise ValueError("File extension must be vcf or vcf.gz")

    with open(inFile, 'rw') as mert:
        sorted_file = "/".join([outdir, file_name + ".sorted.vcf.gz"])

    bcftools.norm("-m", "+any", "-O", "z", "-o",
                  sorted_file, inFile, catch_stdout=False)
    bcftools.index(sorted_file, "-t", "-f", catch_stdout=False)

    return sorted_file


def poolImportVCF((config_file, inputFile)):
    """
    This function is used by multiprocess.Pool to read vcf, populate metadb, and load into tiledb
    """
    with VCF(inputFile, config_file) as vc:
        try:
            # vcf initialization sets up/validates globals (like rs)
            vc.setCallSets()
        except Exception, e:
            traceback.print_exc(file=sys.stdout)
            print "Error processing {0}".format(inputFile)
            print str(e)
            return (-1, inputFile)
        return (0, inputFile, vc.callset_mapping)


def parallelGen(config_file, inputFileList, outputDir):
    """
    Function that spawns the Pool of VCF objects to work on each of the input files
    """
    # set config
    with open(config_file) as conf:
        config = json.load(conf)

    # register reference set, using first vcf
    with open(inputFileList[0], 'rb') as vcf_init:
        reader = vcf.Reader(vcf_init)
        dba, vs, rs = helper.registerWithMetadb(
            config, references=reader.contigs)

    function_args = [None] * len(inputFileList)
    index = 0
    for inFile in inputFileList:
        sorted_file = sortAndIndex(inFile, outputDir)
        function_args[index] = (config_file, sorted_file)
        index += 1

    callset_mapping = dict()
    callset_mapping["callsets"] = dict()
    callsets = callset_mapping["callsets"]

    pool = Pool()
    failed = list()
    for returncode in pool.imap_unordered(poolImportVCF, function_args):
        if returncode[0] == -1:
            failed.append(returncode[1])
        else:
            print "Completed: {0} with {1} Call Sets".format(returncode[1], len(returncode[2]))
            callsets.update(returncode[2])

    if len(failed):
        print "\nERROR: Following files failed to process:"
        for f in failed:
            print "\t{0}".format(f)
        raise Exception("Execution failed on {0}".format(failed))

    helper.createMappingFiles(
        outputDir, callset_mapping, rs.id, config['dburi'])
