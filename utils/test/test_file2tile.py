import pytest
import unittest
import os
import sys
import json
from utils import file2tile

config_path = os.path.join(os.path.realpath(
    sys.argv[-1]), "utils/example_configs/icgc_config.json")
test_header = ["icgc_mutation_id", "project_code", "icgc_donor_id",
               "icgc_sample_id", "matched_icgc_sample_id", "variation_calling_algorithm",
               "assembly_version", "chromosome", "chromosome_start",
               "chromosome_end", "reference_genome_allele", "mutated_to_allele",
               "quality_score", "probability", "total_read_count",
               "mutant_allele_read_count", "chromosome_strand"]
test_data = ["pytest", "ALL-US", "test_person", "target_id", "source_id", "caller",
             "GRCh37", "1", "100", "150", "T", "A", "0.35", "0.9", "100", "90", "0|1"]


class TestFile2Tile(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        with open(config_path, 'r') as readFP:
            config_json = json.load(readFP)
            config_json["TileDBConfig"] = os.path.join(os.path.realpath(
                sys.argv[-1]), "utils/example_configs/tiledb_config.json")
            config_json["TileDBAssembly"] = os.path.join(
                os.path.realpath(sys.argv[-1]), "utils/example_configs/hg19.json")
            config_json["VariantSetMap"]["VariantConfig"] = os.path.join(
                os.path.realpath(sys.argv[-1]), "utils/example_configs/icgc_variants.json")
        with open(config_path, 'w') as writeFP:
            writeFP.write(json.dumps(config_json))

    @pytest.fixture(autouse=True)
    def set_tmpdir(self, tmpdir):
        self.tmpdir = tmpdir

    def test_initFilePointers(self):
        input_file = self.tmpdir.join("in.file")
        input_file.write("# testing\n")
        output_file = self.tmpdir.join("out.file")
        output_file.write("")

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(config_path)
            f2t.initFilePointers(inFP, outFP)

            assert f2t.inFile == inFP
            assert f2t.outFile == outFP
            assert f2t.inFile.closed == False
            assert f2t.outFile.closed == False

            f2t.closeFilePointers()
            assert f2t.inFile.closed == True
            assert f2t.outFile.closed == True
            assert inFP.closed == True
            assert outFP.closed == True

    def test_getHeader(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("\t".join(test_header))
            inFP.write("\n")
        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(config_path)
            f2t.initFilePointers(inFP, outFP)
            assert f2t.header is None
            f2t.getHeader()

            assert isinstance(f2t.header, list)
            assert f2t.header[0] == "icgc_mutation_id"
            assert f2t.header[-1] == "chromosome_strand"

    def test_getHeader_negative_testing(self):
        fields_to_remove = ["icgc_sample_id", "matched_icgc_sample_id", "variation_calling_algorithm",
                            "assembly_version", "chromosome", "chromosome_start",
                            "chromosome_end", "reference_genome_allele", "mutated_to_allele",
                            "quality_score", "probability", "total_read_count",
                            "mutant_allele_read_count", "chromosome_strand"]
        for field_to_remove in fields_to_remove:
            self.helper(field_to_remove, self.tmpdir)

    def helper(self, field_to_remove, tmpdir):
        input_file = tmpdir.join("in.txt")
        # Skip call set header
        incorrect_header = test_header[:]
        incorrect_header.remove(field_to_remove)
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("\t".join(incorrect_header))
            inFP.write("\n")
        output_file = tmpdir.join("out.txt")
        output_file.write("")

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(config_path)
            f2t.initFilePointers(inFP, outFP)
            assert f2t.header is None
            with pytest.raises(ValueError) as exec_info:
                f2t.getHeader()
            assert "{0} is not a valid field in input file's header".format(
                field_to_remove) in str(exec_info.value)

    def test_parseNextLine(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("\t".join(test_header))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(config_path)
            f2t.initFilePointers(inFP, outFP)
            assert f2t.header is None
            f2t.getHeader()
            f2t.parseNextLine()

            assert f2t.IndividualId == test_data[2]
            assert f2t.TargetSampleId == test_data[3]
            assert f2t.SourceSampleId == test_data[4]
            assert f2t.CallSetName == test_data[5]
            assert f2t.VariantSetName == "Blood"
            assert f2t.TileDBPosition == [
                int(test_data[8]) - 1, int(test_data[9]) - 1]
            assert f2t.TileDBValues == dict({"REF": "T", "ALT": ["A"], "QUAL": "0.35",
                                             "AF": ["0.9"], "AN": "100", "AC": ["90"], "GT": ["0|1"]})

            assert f2t.parseNextLine() == False

    def test_parseNextLine_empty_value(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("\t".join(test_header))
            inFP.write("\n")
            empty_qual = test_data[:]
            empty_qual[-2] = ""
            inFP.write("\t".join(empty_qual))
            inFP.write("\n")
        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(config_path)
            f2t.initFilePointers(inFP, outFP)
            assert f2t.header is None
            f2t.parseNextLine()

            assert f2t.IndividualId == test_data[2]
            assert f2t.TargetSampleId == test_data[3]
            assert f2t.SourceSampleId == test_data[4]
            assert f2t.CallSetName == test_data[5]
            assert f2t.VariantSetName == "Blood"
            assert f2t.TileDBPosition == [
                int(test_data[8]) - 1, int(test_data[9]) - 1]
            assert f2t.TileDBValues == dict({"REF": "T", "ALT": ["A"], "QUAL": "0.35",
                                             "AF": ["0.9"], "AN": "100", "AC": ["*"], "GT": ["0|1"]})

    def test_parseNextLine_GT(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("\t".join(test_header))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["Seperators"]["GT"] = "|"
        config_json["GTMapping"]["0"] = "y"
        config_json["GTMapping"]["1"] = "x"
        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(str(test_config))
            f2t.initFilePointers(inFP, outFP)
            assert f2t.header is None
            f2t.getHeader()
            f2t.parseNextLine()

            assert f2t.IndividualId == test_data[2]
            assert f2t.TargetSampleId == test_data[3]
            assert f2t.SourceSampleId == test_data[4]
            assert f2t.CallSetName == test_data[5]
            assert f2t.VariantSetName == "Blood"
            assert f2t.TileDBPosition == [
                int(test_data[8]) - 1, int(test_data[9]) - 1]
            assert f2t.TileDBValues == dict({"REF": "T", "ALT": ["A"], "QUAL": "0.35",
                                             "AF": ["0.9"], "AN": "100", "AC": ["90"], "GT": ["y", "x"]})

    def test_parseNextLine_variantname_static(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("\t".join(test_header))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["VariantSetMap"]["Dynamic"] = False
        config_json["VariantSetMap"]["VariantSet"] = "my_test_variant"
        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(str(test_config))
            f2t.initFilePointers(inFP, outFP)
            assert f2t.header is None
            f2t.getHeader()
            assert f2t.VariantSetName is None
            f2t.parseNextLine()
            f2t.parseNextLine()

            assert f2t.IndividualId == test_data[2]
            assert f2t.TargetSampleId == test_data[3]
            assert f2t.SourceSampleId == test_data[4]
            assert f2t.CallSetName == test_data[5]
            assert f2t.VariantSetName == "my_test_variant"
            assert f2t.TileDBPosition == [
                int(test_data[8]) - 1, int(test_data[9]) - 1]
            assert f2t.TileDBValues == dict({"REF": "T", "ALT": ["A"], "QUAL": "0.35",
                                             "AF": ["0.9"], "AN": "100", "AC": ["90"], "GT": ["0|1"]})

    def test_parseNextLine_variantname_dynamic_name_static_lookup(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("\t".join(test_header))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["VariantSetMap"]["VariantLookup"] = False
        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(str(test_config))
            f2t.initFilePointers(inFP, outFP)
            assert f2t.header is None
            f2t.getHeader()
            f2t.parseNextLine()

            assert f2t.IndividualId == test_data[2]
            assert f2t.TargetSampleId == test_data[3]
            assert f2t.SourceSampleId == test_data[4]
            assert f2t.CallSetName == test_data[5]
            assert f2t.VariantSetName == "ALL-US"
            assert f2t.TileDBPosition == [
                int(test_data[8]) - 1, int(test_data[9]) - 1]
            assert f2t.TileDBValues == dict({"REF": "T", "ALT": ["A"], "QUAL": "0.35",
                                             "AF": ["0.9"], "AN": "100", "AC": ["90"], "GT": ["0|1"]})

    def test_parseNextLine_callset_static(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("\t".join(test_header))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["CallSetId"]["Dynamic"] = False
        config_json["CallSetId"]["CallSetName"] = "my_test_callset"
        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(str(test_config))
            f2t.initFilePointers(inFP, outFP)
            assert f2t.header is None
            f2t.getHeader()
            assert f2t.VariantSetName is None
            f2t.parseNextLine()
            f2t.parseNextLine()

            assert f2t.IndividualId == test_data[2]
            assert f2t.TargetSampleId == test_data[3]
            assert f2t.SourceSampleId == test_data[4]
            assert f2t.CallSetName == "my_test_callset"
            assert f2t.VariantSetName == "Blood"
            assert f2t.TileDBPosition == [
                int(test_data[8]) - 1, int(test_data[9]) - 1]
            assert f2t.TileDBValues == dict({"REF": "T", "ALT": ["A"], "QUAL": "0.35",
                                             "AF": ["0.9"], "AN": "100", "AC": ["90"], "GT": ["0|1"]})

    def test_parseNextLine_assembly_static(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("\t".join(test_header))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["Position"]["assembly"]["Dynamic"] = False
        config_json["Position"]["assembly"]["assemblyName"] = "test_assembly"
        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(str(test_config))
            f2t.initFilePointers(inFP, outFP)
            assert f2t.header is None
            f2t.getHeader()
            assert f2t.VariantSetName is None
            f2t.parseNextLine()
            f2t.parseNextLine()

            assert f2t.ChromosomePosition[0] == "test_assembly"
            assert f2t.IndividualId == test_data[2]
            assert f2t.TargetSampleId == test_data[3]
            assert f2t.SourceSampleId == test_data[4]
            assert f2t.CallSetName == test_data[5]
            assert f2t.VariantSetName == "Blood"
            assert f2t.TileDBPosition == [
                int(test_data[8]) - 1, int(test_data[9]) - 1]
            assert f2t.TileDBValues == dict({"REF": "T", "ALT": ["A"], "QUAL": "0.35",
                                             "AF": ["0.9"], "AN": "100", "AC": ["90"], "GT": ["0|1"]})

    def test_parseNextLine_individual(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("\t".join(test_header))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
            inFP.write("\t".join(test_data))
            inFP.write("\n")
        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(config_path, 'r') as fp:
            config_json = json.load(fp)
        del config_json["IndividualId"]
        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        with open(str(input_file), 'r') as inFP, open(str(output_file), 'w') as outFP:
            f2t = file2tile.File2Tile(str(test_config))
            f2t.initFilePointers(inFP, outFP)
            assert f2t.header is None
            f2t.getHeader()
            assert f2t.VariantSetName is None
            f2t.parseNextLine()
            f2t.parseNextLine()

            assert f2t.IndividualId == "Individual_{0}".format(test_data[4])
            assert f2t.TargetSampleId == test_data[3]
            assert f2t.SourceSampleId == test_data[4]
            assert f2t.CallSetName == test_data[5]
            assert f2t.VariantSetName == "Blood"
            assert f2t.TileDBPosition == [
                int(test_data[8]) - 1, int(test_data[9]) - 1]
            assert f2t.TileDBValues == dict({"REF": "T", "ALT": ["A"], "QUAL": "0.35",
                                             "AF": ["0.9"], "AN": "100", "AC": ["90"], "GT": ["0|1"]})
