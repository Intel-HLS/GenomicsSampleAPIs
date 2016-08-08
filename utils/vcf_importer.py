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

from metadb.api import DBImport
from metadb.models import CallSetToDBArrayAssociation

import utils.helper as helper
import utils.configuration as utils


class VCF:
    """
    Class handling metadb registration and
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
        self.dburi = conf['dburi']
        self.workspace = conf['workspace']
        self.vcf_type = conf['vcf_type']

        self.derive_sample = conf.get('derive_sample_from', 'header')
        self.get_sample_by = conf.get('get_sample_by', None)
        self.get_sample_at = conf.get('get_sample_at', 0)

        # default TN columns normal first column, target second column
        # capture idx in file for GenomicsDB reference
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
            
        if len(self.reader.samples) != 2 and self.vcf_type == 'TN':
            # assume that this is a mixed batch and unset self.vcf_type
            self.vcf_type = None

        if len(self.reader.samples) == 0:
            self.reader.samples = ['']
        
        if self.derive_sample == 'tag':
            if self.get_sample_by is not None:
                self.reader.samples[self.source_idx] = self.reader.metadata['SAMPLE'][self.source_idx][self.get_sample_by]
                if self.vcf_type == 'TN':
                    self.reader.samples[self.target_idx] = self.reader.metadata['SAMPLE'][self.target_idx][self.get_sample_by]
            else:
                raise ValueError('Set get_sample_by for reading sample from tag.')

        if self.derive_sample == 'header':
            if 'NORMAL' in self.reader.samples and self.vcf_type == 'TN':
                raise ValueError("Set derive_sample_from file or tag in import config.")

        if self.derive_sample == 'file':
            if self.get_sample_by is not None:
                sample_prefix = os.path.basename(self.filename).split(self.get_sample_by)[self.get_sample_at]
                if len(self.reader.samples[0]) > 0:
                    sample_prefix += "_"
                self.reader.samples[self.source_idx] = sample_prefix + self.reader.samples[self.source_idx]
                if self.vcf_type == 'TN':
                    self.reader.samples[self.target_idx] = sample_prefix + self.reader.samples[self.target_idx]
            else:
                raise ValueError("Set derive_sample_from file or tag in import config.")


    def createCallSetDict(self):
        """
        Creates a callset dictionary ordered in terms of callset index in vcf
        If callset_loc is not specified, the sample headers are the main identifier
        of the callset. Designed to be later expanded for mulitsample TN vcf, currently
        assumes single sample TN pair VCFs defaulted to NORMAL TUMOUR column order. 
        """

        callsets = OrderedDict()

        self.setSampleNames()

        print self.reader.samples

        callsets[self.reader.samples[self.source_idx]] = self.reader.samples
        if self.vcf_type == 'TN':
            callsets[self.reader.samples[self.target_idx]] = self.reader.samples
 

        return callsets

    def registerCallSets(self):
        """
        Registers CallSets with Metadb and 
        builds callset mapping for GenomicsDB
        """
        callsets = self.createCallSetDict()

        with DBImport(self.dburi).getSession() as metadb:
            for callset in callsets:
                # source and target names
                source = callsets[callset][self.source_idx]

                if callset == source:
                    file_idx = self.source_idx
                else:
                    file_idx = self.target_idx

                # register individual and samples
                indv = metadb.registerIndividual(
                    str(uuid.uuid4()), 
                    "Individual_"+source)

                src = metadb.registerSample(
                    str(uuid.uuid4()),
                    indv.guid,
                    name=source,
                    info={'type': 'source'})

                target_guid = src.guid

                if self.vcf_type == 'TN':
                    target = callsets[callset][self.target_idx]

                    # this is a hack, change the model
                    trg = metadb.registerSample(
                        str(uuid.uuid4()),
                        indv.guid,
                        name=target,
                        info={'type': 'target'})

                    target_guid = trg.guid

                # register callset
                cs = metadb.registerCallSet(str(uuid.uuid4()),
                    src.guid,
                    target_guid,
                    self.workspace,
                    self.array.name,
                    [self.variantset.id],
                    name=callset)

                # retrieve tile row information for callset
                tr = metadb.session.query(CallSetToDBArrayAssociation)\
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
    Used by multiprocess.Pool to read vcf, populate metadb, 
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


def parallelGen(config_file, inputFileList, outputDir, callset_file=None):
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
    helper.createMappingFiles(outputDir, callset_mapping, rs.id, config['dburi'])