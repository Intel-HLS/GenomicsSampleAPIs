import pytest
import json
import os
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, drop_database, database_exists
import metadb.api.query as dbquery
import metadb.models as models
from unittest import TestCase
import utils.vcf2tile as vcimp
from utils.vcf_importer import VCF
import pysam.bcftools


sampleN = 'sampleN'
sampleT = 'sampleT'
test_header = ["#CHROM", "POS", "ID", "REF",
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


class TestVCFImporter(TestCase):

    @classmethod
    def setUpClass(self):
        self.DBURI = "postgresql+psycopg2://@:5432/vcfimport"

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
        self.config_path = os.path.abspath(
            "utils/example_configs/vcf_import.config")
        with open(self.config_path, 'r') as readFP:
            self.config = json.load(readFP)
            self.config["dburi"] = self.DBURI


    @pytest.fixture(autouse=True)
    def set_tmpdir(self, tmpdir):
        self.tmpdir = tmpdir

    def test_end2endVCF(self):
        """
        set vcf sampleIdNormal, sampleIdTumor with no tags
        """
        conf = self.tmpdir.join("vcf1_import.config")
        conf.write(json.dumps(self.config))

        vcfile = self.tmpdir.join("test1.vcf")
        test1_header = list(test_header)
        test1_header.append(sampleN)
        test1_header.append(sampleT)

        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}".format(self.header))
            inVCF.write("{0}\n".format("\t".join(test1_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        vcimp.multiprocess_import.parallelGen(
            str(conf), [str(vcfile)], str(self.tmpdir))

        # check proper import into metadb
        with dbquery.DBQuery(self.DBURI).getSession() as session:
            result = session.session.query(models.CallSet.name) .filter(
                models.CallSet.name.in_([sampleN, sampleT])) .all()
            assert len(result) == 2

        # check callset_map reflects callsets imported
        with open(str(self.tmpdir.join("callset_mapping")), "r") as cmf:
            cm = json.load(cmf)
            assert len(cm['callsets']) == 2

        # check vid_map reflects the contigs in vcf header
        with open(str(self.tmpdir.join("vid_mapping")), "r") as vidf, VCF(str(vcfile), str(conf)) as vc:
            vid = json.load(vidf)
            assert len(vid['contigs']) == len(vc.reader.contigs)

    def test_end2endVCF_neg(self):
        """
        check parallel gen failed execution
        """
        conf = self.tmpdir.join("vcf2_import.config")
        conf.write(json.dumps(self.config))

        vcfile = self.tmpdir.join("test2.vcf")
        test1_header = list(test_header)
        test1_header.append(sampleN)
        test1_header.append(sampleT)
        # execution fails with extra sample
        test1_header.append('extraSample')
        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}\n".format(self.header))
            inVCF.write("{0}\n".format("\t".join(test1_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        with pytest.raises(Exception) as exec_info:
            vcimp.multiprocess_import.parallelGen(
                str(conf), [str(vcfile)], str(self.tmpdir))
        assert "Execution failed" in str(exec_info.value)

    def test_poolImportVCF(self):
        """
        set vcf sampleIdNormal, sampleIdTumor with no tags
        non parallel
        """
        conf = self.tmpdir.join("vcf3_import.config")
        conf.write(json.dumps(self.config))

        vcfile = self.tmpdir.join("test3.vcf")
        test1_header = list(test_header)
        test1_header.append(sampleN)
        test1_header.append(sampleT)
        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}\n".format(self.header))
            inVCF.write("{0}\n".format("\t".join(test1_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        vcimp.multiprocess_import.poolImportVCF((str(conf), str(vcfile)))
        # check proper import
        with dbquery.DBQuery(self.DBURI).getSession() as session:
            result = session.session.query(models.CallSet.name) .filter(
                models.CallSet.name.in_([sampleN, sampleT])) .all()
            assert len(result) == 2

    def test_poolImportVCF_neg(self):
        """
        check pool import vcf failed execution
        """
        conf = self.tmpdir.join("vcf4_import.config")
        conf.write(json.dumps(self.config))

        vcfile = self.tmpdir.join("test4.vcf")
        test1_header = list(test_header)
        test1_header.append(sampleN)
        test1_header.append(sampleT)
        # execution fails with extra sample
        test1_header.append('extraSample')
        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}\n".format(self.header))
            inVCF.write("{0}\n".format("\t".join(test1_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        result = vcimp.multiprocess_import.poolImportVCF(
            (str(conf), str(vcfile)))
        assert result[0] == -1
        # assert result[1] == str(vcfile)

    def test_createCallSetDict_neg(self):
        """
        i) TN vcf, ii) callset_loc in config set, iii) TN vcf with sample tag
        """
        conf = self.tmpdir.join("vcf5_import.config")
        # this_conf = dict(self.config)
        # this_conf['callset_loc'] = None
        conf.write(json.dumps(self.config))

        vcfile = self.tmpdir.join("test5.vcf")
        test1_header = list(test_header)
        test1_header.append(sampleN)
        test1_header.append(sampleT)
        # execution fails with extra sample
        test1_header.append('extraSample')
        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}\n".format(self.header))
            inVCF.write("{0}\n".format("\t".join(test1_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        with pytest.raises(Exception) as exec_info, VCF(str(vcfile), str(conf)) as vc:
            vc.createCallSetDict()
        assert "only single TN" in str(exec_info.value)

        conf = self.tmpdir.join("vcf6_import.config")
        conf.write(json.dumps(self.config))

        vcfile = self.tmpdir.join("test6.vcf")
        test2_header = list(test_header)
        test2_header.append('NORMAL')
        test2_header.append('TUMOUR')
        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}\n".format(self.header))
            inVCF.write("{0}\n".format("\n".join([normal_tag, tumor_tag])))
            inVCF.write("{0}\n".format("\t".join(test2_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        with pytest.raises(Exception) as exec_info, VCF(str(vcfile), str(conf)) as vc:
            vc.createCallSetDict()
        assert "Set callset_loc" in str(exec_info.value)

        conf = self.tmpdir.join("vcf7_import.config")
        this_conf = dict(self.config)
        this_conf['derive_sample_by'] = 'tag'
        this_conf['get_sample_by'] = 'SampleName'
        conf.write(json.dumps(this_conf))

        vcfile = self.tmpdir.join("test7.vcf")
        test3_header = list(test_header)
        test3_header.append('NORMAL')
        test3_header.append('TUMOUR')
        test3_header.append('EXTRA')
        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}\n".format(self.header))
            inVCF.write("{0}\n".format(
                "\n".join([normal_tag, tumor_tag, extra_tag])))
            inVCF.write("{0}\n".format("\t".join(test3_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        with pytest.raises(Exception) as exec_info, VCF(str(vcfile), str(conf)) as vc:
            vc.createCallSetDict()
        assert "only single TN" in str(exec_info.value)

    def test_createCallSetDict(self):

        conf = self.tmpdir.join("vcf8_import.config")
        this_conf = dict(self.config)
        this_conf['derive_sample_by'] = 'tag'
        this_conf['get_sample_by'] = 'SampleName'
        conf.write(json.dumps(this_conf))

        vcfile = self.tmpdir.join("test8.vcf")
        test1_header = list(test_header)
        test1_header.append('NORMAL')
        test1_header.append('TUMOUR')
        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}\n".format(self.header))
            # order of tag in header should reflect order in config
            inVCF.write("{0}\n".format("\n".join([tumor_tag, normal_tag])))
            inVCF.write("{0}\n".format("\t".join(test1_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        with VCF(str(vcfile), str(conf)) as vc:
            results = vc.createCallSetDict()
        assert results[sampleT] == [sampleT, sampleN]
        assert len(results) == 2

    def test_sortAndIndex(self):
        vcfile = self.tmpdir.join("test9.vcf")
        test1_header = list(test_header)
        test1_header.append('NORMAL')
        test1_header.append('TUMOUR')
        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}\n".format(self.header))
            # order of tag in header should reflect order in config
            inVCF.write("{0}\n".format("\n".join([tumor_tag, normal_tag])))
            inVCF.write("{0}\n".format("\t".join(test1_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        vcfilegz = vcimp.multiprocess_import.sortAndIndex(
            str(vcfile), str(self.tmpdir))
        assert 'sorted' in vcfilegz

        testgz = vcimp.multiprocess_import.sortAndIndex(
            str(vcfilegz), str(self.tmpdir))
        assert 'sorted' in testgz

    def test_sortAndIndex_neg(self):
        badvcfile = self.tmpdir.join("test10.vcf.bad")
        testbad_header = list(test_header)
        testbad_header.append('NORMAL')
        testbad_header.append('TUMOUR')
        with open(str(badvcfile), 'w') as inVCF:
            inVCF.write("{0}\n".format(self.header))

        with pytest.raises(Exception) as exec_info:
            fail = vcimp.multiprocess_import.sortAndIndex(
                str(badvcfile), str(self.tmpdir))
        assert "File extension" in str(exec_info.value)

    @classmethod
    def tearDownClass(self):
        drop_database(self.DBURI)
