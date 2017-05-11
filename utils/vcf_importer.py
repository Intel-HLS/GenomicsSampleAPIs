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

import sys
import os
import uuid
import json
import traceback
from multiprocessing import Pool

from collections import OrderedDict, namedtuple

import vcf
import pysam
from pysam import bcftools

from mappingdb.api import DBImport
from mappingdb.models import CallSetToDBArrayAssociation

import utils.helper as helper
import utils.configuration as utils


class VCF:
    """
    Class handling mappingdb registration and
    GenomicsDB loading configuration for a tumor normal VCF file
    """

    def __init__(self, filename, config):
        """
        init reads vcf file name and associated config
        """
        self.filename = filename
        self.configfile = config

        # GenomicsDB loader specific
        self.callset_mapping = dict()

    def __enter__(self):
        """
        VCF opens vcf file as a pyvcf object
        """
        self.file = open(self.filename, 'rb')
        self.reader = vcf.Reader(self.file)

        self.config = open(self.configfile, 'r')
        conf = json.load(self.config)
        self.dburi = utils.getDictValue(conf, 'dburi')
        self.workspace = utils.getDictValue(conf, 'workspace')
        # assume TN pair
        # validate in setSampleNames: single or comp if < 2
        self.vcf_type = conf.get('vcf_type', "TN")

        # how to capture sample name from file
        sample_name_map = conf.get('sample_name', {})
        self.derive_sample = sample_name_map.get('derive_from', 'header')
        self.split_sample_by = sample_name_map.get('split_by', None)
        self.split_sample_index = sample_name_map.get('split_index', 0)

        # set source and target location 
        self.source_idx = conf.get('source_idx', 0)
        self.target_idx = conf.get('target_idx', 1)

        self.array, self.variantset, self.referenceset = helper.registerWithMetadb(
            conf, vcf=True, references=self.reader.contigs)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes file objects used in VCF import
        """
        self.file.close()
        self.config.close()

    def setSampleNames(self):
        """
        Reconstruct pyvcf reader sample list to reflect the callset names desired. 
        """
            
        if len(self.reader.samples) < 2 and self.vcf_type == 'TN':
            # assume that this is a mixed batch and unset self.vcf_type
            self.vcf_type = None
        elif len(self.reader.samples) != 2 and self.vcf_type == 'TN':
            raise ValueError("Currently only single sample, composite, or TN support.")

        # composite vcf
        if len(self.reader.samples) == 0:
            self.reader.samples = ['']
        
        # read sample from sample tag
        if self.derive_sample == 'tag':
            if self.split_sample_by is not None:
                for s in range(0, len(self.reader.samples)):
                    self.reader.samples[s] = self.reader.metadata['SAMPLE'][s][self.split_sample_by]
            else:
                raise ValueError('Set get_sample_by for reading sample from tag.')

        # read sample from file
        if self.derive_sample == 'file':
            sample_prefix = os.path.basename(self.filename).split(self.split_sample_by)[self.split_sample_index]
            for s in range(0, len(self.reader.samples)):
                self.reader.samples[s] = sample_prefix + self.reader.samples[s]


    def createCallSetDict(self):
        """
        Creates a callset dictionary ordered in terms of callset index in vcf.
        """

        callsets = OrderedDict()

        self.setSampleNames()

        for s in range(0, len(self.reader.samples)):
            callsets[self.reader.samples[s]] = self.reader.samples

        return callsets

    def registerCallSets(self):
        """
        Registers CallSets with Metadb and 
        builds callset mapping for GenomicsDB
        """
        callsets = self.createCallSetDict()

        source_idx = self.source_idx 
        target_idx = self.target_idx
        # validate tumor/normal order
        if self.vcf_type == 'TN':
            for i in range(0, len(self.reader.samples)):
                sample = self.reader.samples[i].lower()
                if 'normal' in sample:
                    source_idx = i
                if 'target' in sample or 'primary' in sample:
                    target_idx = i

        with DBImport(self.dburi).getSession() as mappingdb:
            for callset in callsets:
                # source and target names
                source = callsets[callset][source_idx]
                file_idx = source_idx

                # set proper file idex
                if callset != source:
                    file_idx = target_idx

                # register individual and samples
                indv = mappingdb.registerIndividual(
                    str(uuid.uuid4()), 
                    "Individual_"+source)

                src = mappingdb.registerSample(
                    str(uuid.uuid4()),
                    indv.guid,
                    name=source,
                    info={'type': 'source'})

                target_guid = src.guid

                if self.vcf_type == 'TN':
                    target = callsets[callset][target_idx]

                    # need to address change in the mappingdb models
                    trg = mappingdb.registerSample(
                        str(uuid.uuid4()),
                        indv.guid,
                        name=target,
                        info={'type': 'target'})

                    target_guid = trg.guid

                # register callset
                cs = mappingdb.registerCallSet(str(uuid.uuid4()),
                    src.guid,
                    target_guid,
                    self.workspace,
                    self.array.name,
                    [self.variantset.id],
                    name=callset)

                # retrieve tile row information for callset
                tr = mappingdb.session.query(CallSetToDBArrayAssociation)\
                    .filter(CallSetToDBArrayAssociation.callset_id == cs.id)\
                    .first()

                # capture genomics db callset mapping information
                self.callset_mapping[cs.guid] = {
                    'row_idx': tr.tile_row_id,
                    'idx_in_file': file_idx,
                    'filename': self.filename
                }


def sortAndIndex(inFile, outdir, sort=True, index=True):
    """
    Sort and index vcfs to ensure bgzipped, sorted, collapsed and indexed vcfs
    GenomicsDB import will fail if these four requirements aren't satisfied.
    """
    return_file = inFile
    if sort:
        splitFile = os.path.basename(inFile).split(".")
        if splitFile[-1] == 'vcf':
            #.vcf
            file_name = ".".join(splitFile[:-1])
        elif splitFile[-2] == 'vcf' and splitFile[-1] == 'gz':
            # .vcf.gz
            file_name = ".".join(splitFile[:-2])
        else:
            raise ValueError("File extension must be vcf or vcf.gz")

        sorted_file = "/".join([outdir, file_name + ".sorted.vcf.gz"])

        #bcftools sort, collapse, and compress
        bcftools.norm("-m", "+any", "-O", "z", "-o",
                      sorted_file, inFile, catch_stdout=False)
        
        return_file = sorted_file

    if index:
        #bcftools index
        bcftools.index(return_file, "-t", "-f", catch_stdout=False)

    return return_file


def poolImportVCF(file_info):
    """
    Used by multiprocess.Pool to read vcf, populate mappingdb, 
    and (optionally) load into GenomicsDB
    """
    (config_file, inputFile) = file_info
    with VCF(inputFile, config_file) as vc:
        try:
            vc.registerCallSets()
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print "Error processing {0}".format(inputFile)
            print str(e)
            return (-1, inputFile)
        return (0, inputFile, vc.callset_mapping)


def parallelGen(config_file, inputFileList, outputDir, callset_file=None, loader_config=None):
    """
    Spawns the Pool of VCF objects to work on each input VCF
    Creates callset mapping and vid mapping files for GenomicsDB import
    """

    with open(config_file) as conf:
        config = json.load(conf)

    # if no contig information in header, assume it's already registered
    with open(inputFileList[0], 'rb') as vcf_init:
        reader = vcf.Reader(vcf_init)
        dba, vs, rs = helper.registerWithMetadb(config, vcf=True, references=reader.contigs)

    # sort and index vcfs, and
    # build arguments for parallel gen
    function_args = [None] * len(inputFileList)
    index = 0
    for inFile in inputFileList:
        sorted_file = sortAndIndex(inFile, outputDir, sort=config.get('sort_compress',True), index=config.get('index', True))
        function_args[index] = (config_file, sorted_file)
        index += 1

    # append to callset
    if callset_file:
        with open(callset_file) as cf:
            callset_mapping = json.load(cf)
    else:
        callset_mapping = dict()

    callset_mapping["callsets"] = callset_mapping.get("callsets", dict())
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

    # create GenomicsDB vid mapping and callset mapping files 
    helper.createMappingFiles(outputDir, callset_mapping, rs.id, config['dburi'], dba.name, loader_config=loader_config)
