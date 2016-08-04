import pytest
import json
import os
import sys
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, drop_database, database_exists
import metadb.models as models
from unittest import TestCase
import utils.vcf2tile as vcimp
import utils.maf2tile as imp
from utils.configuration import ConfigReader
import ConfigParser
import utils.loader as loader


sampleN = 'sampleN'
sampleT = 'sampleT'
test_header_vcf = ["#CHROM", "POS", "ID", "REF",
               "ALT", "QUAL", "FILTER", "INFO", "FORMAT"]
normal_tag = '##SAMPLE=<ID=NORMAL,Description="Wild type",Platform=ILLUMINA,Protocol=WGS,SampleName=sampleN>'
tumor_tag = '##SAMPLE=<ID=TUMOUR,Description="Mutant",Platform=ILLUMINA,Protocol=WGS,SampleName=sampleT>'
extra_tag = '##SAMPLE=<ID=EXTRA,Description="Mutant",Platform=ILLUMINA,Protocol=WGS,SampleName=extra>'

test_data = [
    "1",
    "10177",
    "rs367896724",
    "A",
    "AC",
    "100",
    "PASS",
    "AC=1;AF=0.425319;AN=6;NS=2504;DP=103152;EAS_AF=0.3363;AMR_AF=0.3602;AFR_AF=0.4909;EUR_AF=0.4056;SAS_AF=0.4949;AA=|||unknown(NO_COVERAGE);VT=INDEL",
    "GT",
    "1|0",
    "0|0"]

test_header_maf = [
    "icgc_mutation_id",
    "project_code",
    "icgc_donor_id",
    "icgc_sample_id",
    "matched_icgc_sample_id",
    "variation_calling_algorithm",
    "assembly_version",
    "chromosome",
    "chromosome_start",
    "chromosome_end",
    "reference_genome_allele",
    "mutated_to_allele",
    "quality_score",
    "probability",
    "total_read_count",
    "mutant_allele_read_count",
    "chromosome_strand"]

test_data = [
    "pytest",
    "ALL-US",
    "test_person",
    "target_id",
    "source_id",
    "caller",
    "GRCh37",
    "1",
    "100",
    "101",
    "T",
    "A",
    "0.35",
    "0.9",
    "100",
    "90",
    "0"]


class TestVMEnd2End(TestCase):

    @classmethod
    def setUpClass(self):
        self.DBURI = "postgresql+psycopg2://@:5432/end2end"

        if database_exists(self.DBURI):
            drop_database(self.DBURI)

        create_database(self.DBURI)

        engine = create_engine(self.DBURI)
        models.bind_engine(engine)

        self.assembly = "testAssembly"

        # test files
        with open("test/data/header.vcf", "r") as f:
            self.header = f.read()

        # create the base config
        self.vcf_config_path = os.path.abspath(
            "utils/example_configs/vcf_import.config")
        with open(self.vcf_config_path, 'r') as readFP:
            self.vcf_config = json.load(readFP)
            self.vcf_config["dburi"] = self.DBURI

        self.maf_config_path = os.path.join(os.path.realpath(
            sys.argv[-1]), "utils/example_configs/icgc_config.json")
        with open(self.maf_config_path, 'r') as readFP:
            config_json = json.load(readFP)
            config_json["TileDBConfig"] = os.path.join(os.path.realpath(
                sys.argv[-1]), "utils/example_configs/tiledb_config.json")
            config_json["TileDBAssembly"] = os.path.join(
                os.path.realpath(sys.argv[-1]), "utils/example_configs/hg19.json")
            config_json["VariantSetMap"]["VariantConfig"] = os.path.join(
                os.path.realpath(sys.argv[-1]), "utils/example_configs/icgc_variants.json")
        with open(self.maf_config_path, 'w') as writeFP:
            writeFP.write(json.dumps(config_json))

        self.maf_config = ConfigReader(self.maf_config_path)
        self.maf_config.DB_URI = self.DBURI
        imp.helper.registerWithMetadb(self.maf_config)

        self.parser = ConfigParser.RawConfigParser()
        self.parser.read('utils/example_configs/load_to_tile.cfg')
        self.parser.set('loader', 'executable', os.path.join(os.path.realpath(
            sys.argv[-1]), "search_library/dependencies/GenomicsDB/bin/vcf2tiledb"))
        self.parser.set('mpi', 'hosts', os.path.join(os.path.realpath(
            sys.argv[-1]), "utils/example_configs/hosts.txt"))

        self.tile_loader_path = os.path.abspath(
            "utils/example_configs/tile_loader.json")
        with open(self.tile_loader_path, 'r') as readFP:
            self.tile_loader = json.load(readFP)
            self.tile_loader['column_partitions'][0]['workspace'] = self.vcf_config['workspace']
            self.tile_loader['column_partitions'][0]['array'] = self.vcf_config['array']



    @pytest.fixture(autouse=True)
    def set_tmpdir(self, tmpdir):
        self.tmpdir = tmpdir

    def test_vmend2end(self):
        """
        end to end testing vcf and maf
        """

        # LOAD VCF

        conf = self.tmpdir.join("vcf_import.config")
        conf.write(json.dumps(self.vcf_config))

        vcfile = self.tmpdir.join("test.vcf")
        test1_header = list(test_header_vcf)
        test1_header.append(sampleN)
        test1_header.append(sampleT)

        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}".format(self.header))
            inVCF.write("{0}\n".format("\t".join(test1_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        vcimp.multiprocess_import.parallelGen(
            str(conf), [str(vcfile)], str(self.tmpdir))

        # check callset_map reflects callsets imported
        with open(str(self.tmpdir.join("callset_mapping")), "r") as cmf:
            cm = json.load(cmf)
            assert len(cm['callsets']) == 2

        # LOAD MAF, with above callset_mapping
        input_file = self.tmpdir.join("in.txt.gz")
        import gzip
        with gzip.open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("{0}\n".format("\t".join(test_header_maf)))
            inFP.write("{0}\n".format("\t".join(test_data)))
        
        with open(self.maf_config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["DB_URI"] = self.DBURI
        config_json["TileDBSchema"]["workspace"] = self.vcf_config["workspace"]
        config_json["TileDBSchema"]["array"] = self.vcf_config["array"]

        test_config = self.tmpdir.join("maf_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        test_output_dir = self.tmpdir.mkdir("output")

        imp.multiprocess_import.parallelGen(
            str(test_config), [
                str(input_file)], str(test_output_dir), True, callset_file=str(self.tmpdir.join("callset_mapping")))

        # check callset_map reflects callsets imported
        with open(str(test_output_dir)+"/callset_mapping", "r") as cmf:
            cm = json.load(cmf)
            assert len(cm['callsets']) == 3
            assert len(cm['unsorted_csv_files']) == 1

        # LOAD INTO GENOMICSDB
        tiledb_loader_file = self.tmpdir.join("tile_loader.json")
        with open(str(tiledb_loader_file), 'w') as fp:
            fp.write(json.dumps(self.tile_loader))

        self.parser.set('loader', 'tile_loader_json', str(tiledb_loader_file))
        loader_config = self.tmpdir.join("loader_config.cfg")
        with open(str(loader_config), 'w') as fp:
            self.parser.write(fp)

        # loader.load2Tile(str(loader_config), str(test_output_dir)+"/callset_mapping", str(test_output_dir)+"/vid_mapping")

    @classmethod
    def tearDownClass(self):
        drop_database(self.DBURI)
