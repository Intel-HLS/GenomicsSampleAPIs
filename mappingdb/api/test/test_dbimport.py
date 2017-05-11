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

import pytest
import uuid
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy_utils import create_database, drop_database, database_exists
import mappingdb.api.dbimport as dbimport
import mappingdb.models as models
from unittest import TestCase
import vcf

sampleN = 'sampleN'
sampleT = 'sampleT'
test_header = ["#CHROM", "POS", "ID", "REF",
               "ALT", "QUAL", "FILTER", "INFO", "FORMAT"]
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


class TestDBImportLevel0(TestCase):
    """
    Tests all MetaDB Parent Object registration:
      Level 0 of the MetaDB relationship hierarchy
    """

    @classmethod
    def setUpClass(self):
        self.DBURI = "postgresql+psycopg2://@:5432/dbimport"

        if database_exists(self.DBURI):
            drop_database(self.DBURI)

        create_database(self.DBURI)

        engine = create_engine(self.DBURI)
        models.bind_engine(engine)

        self.assembly = "testAssembly"
        self.workspace = "/test/dbimport/workspace"

    def test_registerReferenceSet(self):

        rguid = str(uuid.uuid4())
        r2guid = str(uuid.uuid4())
        fguid = rguid + '-longer'

        with dbimport.DBImport(self.DBURI).getSession() as session:
            # register new
            result = session.registerReferenceSet(rguid, self.assembly)
            assert result.assembly_id == self.assembly
            assert result.guid == rguid

            # registering an already registered referenceset, by assembly
            reg_result = session.registerReferenceSet(r2guid, self.assembly)
            assert reg_result.assembly_id == self.assembly
            assert reg_result.guid == rguid

            # registering an already registered referenceset, by guid
            session.registerReferenceSet(rguid, 'hg19')
            assert reg_result.assembly_id == self.assembly
            assert reg_result.guid == rguid

            # verify only one reference set exists
            num_rs = session.session.query(models.ReferenceSet).count()
            assert num_rs == 1

            # negative test
            with pytest.raises(ValueError) as exec_info:
                session.registerReferenceSet(fguid, "negAssembly")
            assert "DataError" in str(exec_info.value)

    def test_registerWorkspace(self):

        wguid = str(uuid.uuid4())
        fguid = wguid + "-longer"

        with dbimport.DBImport(self.DBURI).getSession() as session:

            # new with path consistency
            result = session.registerWorkspace(wguid, self.workspace + "/")
            assert result.name == self.workspace
            assert result.name[-1] != "/"

            # registered
            reg_result = session.registerWorkspace(wguid, self.workspace)
            assert reg_result.name == self.workspace
            assert reg_result.guid == wguid

            # negative
            with pytest.raises(ValueError) as exec_info:
                neg_result = session.registerWorkspace(
                    fguid, "negative/workspace")
            assert "DataError" in str(exec_info.value)

    def test_registerIndividual(self):

        iguid = str(uuid.uuid4())
        i2guid = str(uuid.uuid4())
        fguid = iguid + "-longer"

        with dbimport.DBImport(self.DBURI).getSession() as session:

            # new
            result = session.registerIndividual(iguid, name="testIndividual")
            assert result.name == "testIndividual"
            assert result.guid == iguid

            # not new, by name
            reg_result = session.registerIndividual(
                i2guid, name="testIndividual")
            assert reg_result.name == "testIndividual"
            assert reg_result.guid == iguid

            # now new, by guid
            result = session.registerIndividual(iguid, name="DO76")
            assert result.name == "testIndividual"
            assert result.guid == iguid

            # negative
            with pytest.raises(ValueError) as exec_info:
                not_none = session.registerIndividual(fguid, name="None")
            assert 'DataError' in str(exec_info.value)

            with pytest.raises(ValueError) as exec_info:
                neg_result = session.registerIndividual(
                    str(uuid.uuid4()), name=None)
            assert 'IntegrityError' in str(exec_info.value)

    @classmethod
    def tearDownClass(self):
        drop_database(self.DBURI)


class TestDBImportLevel1(TestCase):
    """
    Tests all MetaDB Child Object Registration
      Level 1 of the MetaDB relationship hierarchy
    """
    @pytest.fixture(autouse=True)
    def set_tmpdir(self, tmpdir):
        self.tmpdir = tmpdir

    @classmethod
    def setUpClass(self):
        self.DBURI = "postgresql+psycopg2://@:5432/dbimport"

        if database_exists(self.DBURI):
            drop_database(self.DBURI)

        create_database(self.DBURI)

        engine = create_engine(self.DBURI)
        models.bind_engine(engine)

        self.references = {"1": 249250621, "2": 243199373, "3": 198022430}
        self.array = "test"

        # referenceset, workspace, and individual registration previously
        # tested
        with dbimport.DBImport(self.DBURI).getSession() as session:
            self.referenceset = session.registerReferenceSet(
                str(uuid.uuid4()), "testAssembly", references=self.references)
            self.workspace = session.registerWorkspace(
                str(uuid.uuid4()), "/test/dbimport/workspace")
            self.individual = session.registerIndividual(
                str(uuid.uuid4()), name="testIndividual")

    def test_sortReferences(self):

        # get a pyvcf contig dict
        with open("test/data/header.vcf", "r") as f:
            header = f.read()

        vcfile = self.tmpdir.join("test1.vcf")
        test1_header = list(test_header)
        test1_header.append(sampleN)
        test1_header.append(sampleT)

        with open(str(vcfile), 'w') as inVCF:
            inVCF.write("{0}".format(header))
            inVCF.write("{0}\n".format("\t".join(test1_header)))
            inVCF.write("{0}\n".format("\t".join(test_data)))

        with open(str(vcfile), 'r') as f:
            r = vcf.Reader(f)
            self.contigs = r.contigs

        result1 = dbimport.sortReferences(
            {"1": 249250621, "2": 243199373, "3": 198022430, "MT": 1000})
        assert result1.get('MT', None) is None
        assert result1.get('M', None) is not None

        result2 = dbimport.sortReferences(self.contigs)
        assert result2 == self.contigs

    def test_registerReference(self):

        rguid = str(uuid.uuid4())
        r2guid = str(uuid.uuid4())
        mguid = str(uuid.uuid4())
        fguid = rguid + "-longer"

        with dbimport.DBImport(self.DBURI).getSession() as session:

                # regsiter with references
            result = session.registerReferenceSet(
                self.referenceset.guid,
                self.referenceset.assembly_id,
                references=self.references)
            assert result.assembly_id == self.referenceset.assembly_id
            assert result.guid == self.referenceset.guid

            # validate all references were registered
            refs = session.session.query(
                models.Reference).filter(
                models.Reference.reference_set_id == result.id,
                models.Reference.name.in_(
                    self.references.keys())).all()
            assert len(refs) == len(self.references)

            # register a single reference
            result2 = session.registerReference(
                r2guid, self.referenceset.id, "4", 191154276)
            assert result2.name == "4"
            assert result2.length == 191154276

            # validate MT -> M
            resultM = session.registerReference(
                mguid, self.referenceset.id, "MT", 16571)
            assert resultM.name == "M"
            assert resultM.guid == mguid

            # validate return of registered reference given reference set id
            # and reference name
            reg_result = session.registerReference(
                str(uuid.uuid4()), self.referenceset.id, "M", 16000)
            assert reg_result.name == "M"
            assert reg_result.guid == mguid

            # negative
            with pytest.raises(ValueError) as exec_info:
                neg_result = session.registerReference(
                    fguid, self.referenceset.id, "5", 180915260)
            assert "DataError" in str(exec_info.value)

    def test_registerReferenceOffset(self):
        with dbimport.DBImport(self.DBURI).getSession() as session:
            # get chr4 and validate offset
            # separate test (since sqlalchemy won't update until previous test
            # finishes)
            result = session.registerReference(
                str(uuid.uuid4()), self.referenceset.id, "4", 191154276)
            assert result.tiledb_column_offset == 759519666

    def test_registerDBArray(self):

        aguid = str(uuid.uuid4())
        fguid = aguid + "-longer"

        with dbimport.DBImport(self.DBURI).getSession() as session:

            # new array
            result = session.registerDBArray(
                aguid, self.referenceset.id, self.workspace.id, self.array)
            assert result.name == self.array
            assert result.guid == aguid

            # registered array
            reg_result = session.registerDBArray(
                str(uuid.uuid4()), self.referenceset.id, self.workspace.id, self.array)
            assert reg_result.name == self.array
            assert reg_result.guid == aguid

            # negative
            with pytest.raises(ValueError) as exec_info:
                neg_result = session.registerDBArray(
                    fguid, self.referenceset.id, self.workspace.id, "negative")
            assert "DataError" in str(exec_info.value)

    def test_registerSample(self):

        sguid = str(uuid.uuid4())
        s2guid = str(uuid.uuid4())
        fguid = sguid + "-longer"
        figuid = str(uuid.uuid4()) + "-longer"

        with dbimport.DBImport(self.DBURI).getSession() as session:
            # new sample
            result = session.registerSample(
                sguid, self.individual.guid, name="testSample")
            assert result.guid == sguid
            assert result.name == "testSample"

            # registered, get by individual id and name
            reg_result = session.registerSample(
                s2guid, self.individual.guid, name="testSample")
            assert reg_result.guid == sguid
            assert reg_result.name == "testSample"

            # registered, get by guid
            reg2_result = session.registerSample(
                sguid, self.individual.guid, name="alreadyreg")
            assert reg2_result.guid == sguid
            assert reg2_result.name == "testSample"

            # negative
            with pytest.raises(ValueError) as exec_info:
                neg_result = session.registerSample(
                    fguid, self.individual.guid, name="negative")
            assert "DataError" in str(exec_info.value)

            # negative individual guid
            with pytest.raises(ValueError) as exec_info:
                negI_result = session.registerSample(
                    sguid, figuid, name="negativeIndividual")
            assert "Invalid Individual Id" in str(exec_info.value)

    def test_registerVariantSet(self):

        vguid = str(uuid.uuid4())
        fguid = vguid + "-longer"

        with dbimport.DBImport(self.DBURI).getSession() as session:
            # new
            result = session.registerVariantSet(
                vguid, self.referenceset.id, "Dataset")
            assert result.guid == vguid
            assert result.reference_set_id == 1

            # registered, return by guid
            reg_result = session.registerVariantSet(
                vguid, self.referenceset.id, "AlreadyReg")
            assert reg_result.guid == vguid
            assert reg_result.dataset_id == "Dataset"

            # negative
            with pytest.raises(ValueError) as exec_info:
                result = session.registerVariantSet(
                    fguid, self.referenceset.id, "negative")
            assert "DataError" in str(exec_info.value)

            # negative referenceset
            with pytest.raises(ValueError) as exec_info:
                result = session.registerVariantSet(vguid, -1, "negative_rs")
            assert "must be registered" in str(exec_info.value)

    @classmethod
    def tearDownClass(self):
        drop_database(self.DBURI)


class TestDBImportLevel2(TestCase):
    """
    Test Registration of CallSet - dependent on most other models
    """

    @classmethod
    def setUpClass(self):
        self.DBURI = "postgresql+psycopg2://@:5432/dbimport"

        if database_exists(self.DBURI):
            drop_database(self.DBURI)

        create_database(self.DBURI)

        engine = create_engine(self.DBURI)
        models.bind_engine(engine)

        # all these function have been previously tested
        with dbimport.DBImport(self.DBURI).getSession() as session:

            self.referenceset = session.registerReferenceSet(
                str(uuid.uuid4()), "testAssembly")
            self.workspace = session.registerWorkspace(
                str(uuid.uuid4()), "/test/dbimport/workspace")
            self.array = session.registerDBArray(
                str(uuid.uuid4()), self.referenceset.id, self.workspace.id, "test")
            self.array2 = session.registerDBArray(
                str(uuid.uuid4()), self.referenceset.id, self.workspace.id, "test2")

            self.variantset = session.registerVariantSet(
                str(uuid.uuid4()), self.referenceset.id, "Dataset")
            self.variantset2 = session.registerVariantSet(
                str(uuid.uuid4()), self.referenceset.id, "Dataset2")
            self.variantset3 = session.registerVariantSet(
                str(uuid.uuid4()), self.referenceset.id, "Dataset3")
            self.variantset4 = session.registerVariantSet(
                str(uuid.uuid4()), self.referenceset.id, "Dataset4")

            self.individual = session.registerIndividual(
                str(uuid.uuid4()), name="testIndividual")
            self.source = session.registerSample(
                str(uuid.uuid4()), self.individual.guid, name="source")
            self.target = session.registerSample(
                str(uuid.uuid4()), self.individual.guid, name="target")

    def test_registerCallSet(self):

        cguid = str(uuid.uuid4())
        c2guid = str(uuid.uuid4())
        fguid = cguid + "-longer"

        with dbimport.DBImport(self.DBURI).getSession() as session:

            # no variant set
            with pytest.raises(ValueError) as exec_info:
                result = session.registerCallSet(
                    cguid,
                    self.source.guid,
                    self.target.guid,
                    self.workspace.name,
                    self.array.name,
                    name="CallSet1")
            assert "requires association" in str(exec_info)

            # register new, validate addition of that variant set
            result = session.registerCallSet(
                cguid,
                self.source.guid,
                self.target.guid,
                self.workspace.name,
                self.array.name,
                name="CallSet1",
                variant_set_ids=[
                    self.variantset.id])
            assert result.variant_sets[0].id == self.variantset.id
            assert result.guid == cguid
            assert result.name == "CallSet1"

            # add a variant set to callset, validation of no duplication of
            # variant set addition
            result_vs = session.registerCallSet(
                cguid,
                self.source.guid,
                self.target.guid,
                self.workspace.name,
                self.array.name,
                name="CallSet1",
                variant_set_ids=[
                    self.variantset.id])
            assert result_vs.variant_sets[0].id == self.variantset.id
            assert len(result_vs.variant_sets) == 1
            assert result_vs.guid == cguid

            # add a variant set to callset, validation of no duplication of
            # variant set addition
            with pytest.raises(ValueError) as exec_info:
                result_vs3 = session.registerCallSet(
                    cguid,
                    self.source.guid,
                    self.target.guid,
                    self.workspace.name,
                    self.array.name,
                    name="CallSet1",
                    variant_set_ids=[5])
            assert "VariantSet must be registered" in str(exec_info.value)

            # already registered, return based on (name, source sample, target
            # sample)
            reg_result = session.registerCallSet(
                c2guid,
                self.source.guid,
                self.target.guid,
                self.workspace.name,
                self.array.name,
                name="CallSet1")
            assert reg_result.guid == cguid
            assert reg_result.name == "CallSet1"

            # already registered, return based on guid
            reg2_result = session.registerCallSet(
                cguid,
                self.source.guid,
                self.target.guid,
                self.workspace.name,
                self.array.name,
                name="CallSetRegistered")
            assert reg2_result.guid == cguid
            assert reg2_result.name == "CallSet1"

            # validate workspace remove ending "/"
            reg_ws_result = session.registerCallSet(
                cguid,
                self.source.guid,
                self.target.guid,
                self.workspace.name + "/",
                self.array.name,
                name="CallSet1")
            assert reg_ws_result.guid == cguid
            assert reg_ws_result.name == "CallSet1"

            # check db array reg error
            with pytest.raises(ValueError) as exec_info:
                reg_a_result = session.registerCallSet(
                    cguid,
                    self.source.guid,
                    self.target.guid,
                    self.workspace.name,
                    "notregistered",
                    name="CallSet1")
            assert "DBArray needs to exist" in str(exec_info.value)

            # register callset to a new array
            reg_a2_result = session.registerCallSet(
                cguid,
                self.source.guid,
                self.target.guid,
                self.workspace.name,
                self.array2.name,
                name="CallSet1")
            assert reg_a2_result.guid == cguid
            assert reg_a2_result.name == "CallSet1"

            # validate callset registration to that array
            ca = session.session.query(models.CallSetToDBArrayAssociation) .filter(
                models.CallSetToDBArrayAssociation.db_array_id == self.array2.id) .all()
            assert len(ca) == 1
            assert ca[0].callset_id == reg_a2_result.id

            # negative callset registration
            with pytest.raises(ValueError) as exec_info:
                neg_result = session.registerCallSet(
                    fguid,
                    self.source.guid,
                    self.target.guid,
                    self.workspace.name,
                    self.array.name,
                    name="negative",
                    variant_set_ids=[
                        self.variantset.id])
            assert "DataError" in str(exec_info.value)

            # negative callset registration - invalid sample_guid
            with pytest.raises(ValueError) as exec_info:
                negs_result = session.registerCallSet(str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4(
                )), self.workspace.name, self.array.name, name="negative", variant_set_ids=[self.variantset.id])
            assert "Issue retrieving Sample info" in str(exec_info.value)

            # test update variant set list
            vsl_result = session.updateVariantSetList(
                [1, 2, 3], callset=result)
            assert [x.id for x in vsl_result.variant_sets] == [
                self.variantset.id, self.variantset2.id, self.variantset3.id]

            # test update variant sets through registerCallSet
            c_result = session.registerCallSet(
                cguid,
                self.source.guid,
                self.target.guid,
                self.workspace.name,
                self.array.name,
                name="CallSet1",
                variant_set_ids=[
                    self.variantset3.id,
                    self.variantset4.id])
            assert self.variantset4.id == c_result.variant_sets[-1].id

    @classmethod
    def tearDownClass(self):
        drop_database(self.DBURI)
