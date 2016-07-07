import pytest
import unittest
import os
import sys
import json
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, database_exists
from metadb import models
import utils.maf2tile as imp
from utils.csvline import CSVLine
from metadb.api.query import DBQuery
from utils.configuration import ConfigReader

test_header = [
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


class TestMAF(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.TESTDB_URI = "postgresql+psycopg2://@:5432/mafend2end"
        if not database_exists(self.TESTDB_URI):
            create_database(self.TESTDB_URI)

        engine = create_engine(self.TESTDB_URI)
        models.bind_engine(engine)
        self.config_path = os.path.join(os.path.realpath(
            sys.argv[-1]), "utils/example_configs/icgc_config.json")
        with open(self.config_path, 'r') as readFP:
            config_json = json.load(readFP)
            config_json["TileDBConfig"] = os.path.join(os.path.realpath(
                sys.argv[-1]), "utils/example_configs/tiledb_config.json")
            config_json["TileDBAssembly"] = os.path.join(
                os.path.realpath(sys.argv[-1]), "utils/example_configs/hg19.json")
            config_json["VariantSetMap"]["VariantConfig"] = os.path.join(
                os.path.realpath(sys.argv[-1]), "utils/example_configs/icgc_variants.json")
        with open(self.config_path, 'w') as writeFP:
            writeFP.write(json.dumps(config_json))

        config = ConfigReader(self.config_path)
        config.DB_URI = self.TESTDB_URI
        imp.helper.registerWithMetadb(config)

    @pytest.fixture(autouse=True)
    def set_tmpdir(self, tmpdir):
        self.tmpdir = tmpdir

    def test_end2end(self):
        csvlines = dict()
        input_file = self.tmpdir.join("in.txt")
        db = DBQuery("postgresql+psycopg2://@:5432/metadb")
        with open(str(input_file), 'w') as inFP, db.getSession() as metadb:
            inFP.write("# Comment line\n")
            inFP.write("{0}\n".format("\t".join(test_header)))
            inFP.write("{0}\n".format("\t".join(test_data)))
            # Repeat the same line a couple of times
            inFP.write("{0}\n".format("\t".join(test_data)))
            inFP.write("{0}\n".format("\t".join(test_data)))
            csvlines[0] = [self.getCSVLine(test_data, 0)]
            # Introduce new Source Sample
            new_data = self.setAndGet(
                test_data, "matched_icgc_sample_id", "source_id1")
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            csvlines[1] = [self.getCSVLine(new_data, 1)]
            # Introduce new Target Sample
            new_data = self.setAndGet(new_data, "icgc_sample_id", "target_id1")
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            csvlines[2] = [self.getCSVLine(new_data, 2)]
            # Introduce new callset
            new_data = self.setAndGet(
                new_data, "variation_calling_algorithm", "caller1")
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            csvlines[3] = [self.getCSVLine(new_data, 3)]
            # Introduce new individual
            new_data = self.setAndGet(
                new_data, "icgc_donor_id", "test_person1")
            new_data = self.setAndGet(
                new_data, "matched_icgc_sample_id", "source_id_tp1")
            new_data = self.setAndGet(
                new_data, "icgc_sample_id", "target_id_tp1")
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            # Introduce new ALT, GT for the same sample
            new_data = self.setAndGet(new_data, "mutated_to_allele", "G")
            new_data = self.setAndGet(new_data, "chromosome_strand", "1")
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            csvlines[4] = [self.getCSVLine(
                new_data, 4, ALT=["A", "G"], GT=["0", "2"])]
            # Introduce REF with '-', change to new tile row
            new_data = self.setAndGet(
                test_data, "matched_icgc_sample_id", "source_id2")
            new_data = self.setAndGet(new_data, "reference_genome_allele", "-")
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            csvlines[5] = [self.getCSVLine(new_data, 5, Location=(
                99 - 1), End=(99 - 1), REF="N", ALT=["NA"])]
            # Introduce REF with '-', change to new tile row
            new_data = self.setAndGet(
                test_data, "matched_icgc_sample_id", "source_id3")
            new_data = self.setAndGet(new_data, "mutated_to_allele", "-")
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            csvlines[6] = [self.getCSVLine(
                new_data, 6, Location=(99 - 1), REF="NT", ALT=["N"])]
            # Introduce new chromosome, change to new tile row
            contigs = [str(i) for i in range(2, 23)]
            #contigs.extend(["X", "Y", "M"])
            contigs.extend(["M", "X", "Y"])
            new_data = self.setAndGet(
                test_data, "icgc_donor_id", "test_person2")
            new_data = self.setAndGet(
                new_data, "matched_icgc_sample_id", "source_id_tp2")
            new_data = self.setAndGet(
                new_data, "icgc_sample_id", "target_id_tp2")
            new_data = self.setAndGet(new_data, "chromosome_start", "600")
            new_data = self.setAndGet(new_data, "chromosome_end", "601")
            csvlines[7] = list()
            for contig in contigs:
                new_data = self.setAndGet(new_data, "chromosome", contig)
                inFP.write("{0}\n".format("\t".join(new_data)))
                inFP.write("{0}\n".format("\t".join(new_data)))
                inFP.write("{0}\n".format("\t".join(new_data)))
                Location, End = metadb.contig2Tile(
                    1, contig, [long(new_data[8]), long(new_data[9])])
                csvlines[7].append(self.getCSVLine(
                    new_data, 7, Location=Location, End=End))
            # Repeat the same test_data line a couple of times
            inFP.write("{0}\n".format("\t".join(test_data)))
            inFP.write("{0}\n".format("\t".join(test_data)))
            inFP.write("{0}\n".format("\t".join(test_data)))
            # Add new data to existing sample at different position
            new_data = self.setAndGet(test_data, "chromosome_start", "600")
            new_data = self.setAndGet(new_data, "chromosome_end", "601")
            new_data = self.setAndGet(new_data, "chromosome", "2")
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            Location, End = metadb.contig2Tile(
                1, "2", [long(new_data[8]), long(new_data[9])])
            csvlines[0].append(self.getCSVLine(
                new_data, 0, Location=Location, End=End))
            # Introduce the prev new Source Sample but with different ALT
            new_data = self.setAndGet(
                test_data, "matched_icgc_sample_id", "source_id1")
            new_data = self.setAndGet(new_data, "mutated_to_allele", "G")
            new_data = self.setAndGet(new_data, "chromosome_strand", "1")
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            inFP.write("{0}\n".format("\t".join(new_data)))
            csvlines[1] = [self.getCSVLine(
                new_data, 1, ALT=["A", "G"], GT=["-1", "-1"])]

        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(self.config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["DB_URI"] = self.TESTDB_URI

        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        test_output_dir = self.tmpdir.mkdir("output")

        imp.multiprocess_import.poolGenerateCSV((str(test_config), str(
            input_file), str(test_output_dir) + "/" + "out.txt", False))

        total_csv_lines = 0
        for tile_sample in csvlines.values():
            total_csv_lines += len(tile_sample)

        verified_csv_lines = 0
        output_file = test_output_dir.join("out.txt")
        with open(str(output_file), 'r') as outputFP:
            while True:
                line = outputFP.readline().strip()
                if len(line) == 0:
                    break
                index = int(line.split(',')[0])
                if len(csvlines[index]) == 1:
                    assert line == csvlines[index][0]
                    verified_csv_lines += 1
                else:
                    found = False
                    for expected in csvlines[index]:
                        if expected == line:
                            found = True
                            verified_csv_lines += 1
                            break
                    assert found, [line, index, csvlines[index]]
            assert total_csv_lines == verified_csv_lines

    def test_poolGenerateCSV_neg(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("{0}\n".format("\t".join(test_header)))
            inFP.write("{0}\n".format("\t".join(test_data)))
            # Repeat the same line but only partially
            inFP.write("{0}\n".format("\t".join(test_data[0:8])))

        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(self.config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["DB_URI"] = self.TESTDB_URI

        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        test_output_dir = self.tmpdir.mkdir("output")

        result = imp.multiprocess_import.poolGenerateCSV((str(test_config), str(
            input_file), str(test_output_dir) + '/' + "out.txt", False))
        assert result[0] == -1
        assert result[1] == str(input_file)

    def test_poolGenerateCSV_gzip(self):
        input_file = self.tmpdir.join("in.txt.gz")
        import gzip
        with gzip.open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("{0}\n".format("\t".join(test_header)))
            inFP.write("{0}\n".format("\t".join(test_data)))

        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(self.config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["DB_URI"] = self.TESTDB_URI

        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        test_output_dir = self.tmpdir.mkdir("output")

        imp.multiprocess_import.poolGenerateCSV((str(test_config), str(
            input_file), str(test_output_dir) + '/' + "out.txt", True))

        output_file = test_output_dir.join("out.txt")
        with open(str(output_file), 'r') as outputFP:
            line = outputFP.readline().strip()
        assert line == self.getCSVLine(test_data, 0)

    def test_end2end_gzip(self):
        input_file = self.tmpdir.join("in.txt.gz")
        import gzip
        with gzip.open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("{0}\n".format("\t".join(test_header)))
            inFP.write("{0}\n".format("\t".join(test_data)))

        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(self.config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["DB_URI"] = self.TESTDB_URI
        config_json["TileDBSchema"]["array"] = "test_end2end_gzip"

        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        test_output_dir = self.tmpdir.mkdir("output")

        imp.multiprocess_import.parallelGen(
            str(test_config), [
                str(input_file)], str(test_output_dir), "out.txt", True)

        output_file = test_output_dir.join("out.txt")
        with open(str(output_file), 'r') as outputFP:
            line = outputFP.readline().strip()
        assert line == self.getCSVLine(test_data, 0)

    def test_end2end_neg(self):
        input_file = self.tmpdir.join("in.txt")
        with open(str(input_file), 'w') as inFP:
            inFP.write("# Comment line\n")
            inFP.write("{0}\n".format("\t".join(test_header)))
            inFP.write("{0}\n".format("\t".join(test_data)))
            # Repeat the same line but only partially
            inFP.write("{0}\n".format("\t".join(test_data[0:8])))

        output_file = self.tmpdir.join("out.txt")
        output_file.write("")

        with open(self.config_path, 'r') as fp:
            config_json = json.load(fp)
        config_json["DB_URI"] = self.TESTDB_URI
        config_json["TileDBSchema"]["array"] = "test_end2end"

        test_config = self.tmpdir.join("test_config.json")
        with open(str(test_config), 'w') as fp:
            fp.write(json.dumps(config_json))

        test_output_dir = self.tmpdir.mkdir("output")

        with pytest.raises(Exception) as exec_info:
            imp.multiprocess_import.parallelGen(str(test_config), [str(
                input_file)], str(test_output_dir), "out.txt", False)
        assert "Execution failed" in str(exec_info.value)

    def getCSVLine(self, input_list, SampleId,
                   Location=None, End=None, REF=None, ALT=None, GT=None):
        csv_line = CSVLine()
        csv_line.set("SampleId", SampleId)
        if Location is None:
            csv_line.set("Location", str(long(input_list[8]) - 1))
        else:
            csv_line.set("Location", Location)
        if End is None:
            csv_line.set("End", str(long(input_list[9]) - 1))
        else:
            csv_line.set("End", End)
        if REF is None:
            csv_line.set("REF", input_list[10])
        else:
            csv_line.set("REF", REF)
        if ALT is None:
            csv_line.set("ALT", [input_list[11]])
            csv_line.set("AF", [input_list[13]])
            csv_line.set("AC", [input_list[15]])
        else:
            csv_line.set("ALT", ALT)
            AF = [input_list[13]]
            AC = [input_list[15]]
            for x in xrange(1, len(ALT)):
                AF.append(input_list[13])
                AC.append(input_list[15])
            csv_line.set("AF", AF)
            csv_line.set("AC", AC)
        csv_line.set("QUAL", input_list[12])
        csv_line.set("AN", input_list[14])
        csv_line.set("PLOIDY", 2)
        if GT is None:
            csv_line.set("GT", [input_list[16], "0"])
        else:
            csv_line.set("GT", GT)
        return csv_line.getCSVLine()

    def setAndGet(self, input_list, header_field, newValue):
        new_data = input_list[:]
        index = test_header.index(header_field)
        new_data[index] = newValue
        return new_data
