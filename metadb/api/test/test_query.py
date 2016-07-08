import pytest
import metadb.api.query as query
import metadb.models as models


class TestQuery:
    DBURI = "postgresql+psycopg2://@:5432/metadb"
    workspace = "/home/variantdb/DB"
    arrayName = "test"
    numRows = 8
    chromosomes = ["1", "2", "3", "4", "5", "6", "7",
                   "8", "9", "10", "11", "12", "13", "14",
                   "15", "16", "17", "18", "19", "20", "21",
                   "22", "X", "Y", "M"]
    chromosome_lengths = {
        "1": 249250621,
        "2": 243199373,
        "3": 198022430,
        "4": 191154276,
        "5": 180915260,
        "6": 171115067,
        "7": 159138663,
        "8": 146364022,
        "9": 141213431,
        "10": 135534747,
        "11": 135006516,
        "12": 133851895,
        "13": 115169878,
        "14": 107349540,
        "15": 102531392,
        "16": 90354753,
        "17": 81195210,
        "18": 78077248,
        "19": 59128983,
        "20": 63025520,
        "21": 48129895,
        "22": 51304566,
        "X": 155270560,
        "Y": 59373566,
        "M": 16571}
    dataset_id = "TileDB"

    def typeCheck(self, result, objectType, objectValueType, length):
        assert isinstance(result, objectType)
        assert len(result) == length
        if length > 0:
            assert isinstance(result[0], objectValueType)

    def test_individualId2Name_single_idx(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            idx = 1
            result = session.individualId2Name(idx)
            self.typeCheck(result, list, unicode, 1)

    def test_individualId2Name_range_idx(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            # Using range that is greater than # samples in the test db
            idx = range(1, self.numRows + 2)
            result = session.individualId2Name(idx)
            self.typeCheck(result, list, unicode, len(idx))
            assert result[-1] is None

    def test_individualName2Id_single_idx(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            idx = 1
            name = session.individualId2Name(idx)[0]
            result = session.individualName2Id(name)
            self.typeCheck(result, list, long, 1)
            assert result[0] == idx

    def test_individualName2Id_range_idx(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            # Using range that is greater than # samples in the test db
            idx = range(1, self.numRows + 2)
            name = session.individualId2Name(idx)[0:4]
            name.append("invalid_name")
            result = session.individualName2Id(name)
            self.typeCheck(result, list, long, len(name))
            assert result[0] == idx[0]
            assert result[-1] is None

    def test_arrayId2TileNames(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            idx = 1
            result = session.arrayId2TileNames(idx)
            assert result[0] == self.workspace
            assert result[1] == self.arrayName

    def test_arrayId2TileNames_neg_test(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            idx = 10
            with pytest.raises(ValueError) as exec_info:
                session.arrayId2TileNames(idx)
            # assert result[0] == "/home/variantdb/DB"
            assert "Invalid Array Id" in str(exec_info.value)

    def test_tileNames2ArrayIdx(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            result = session.tileNames2ArrayIdx(self.workspace, self.arrayName)
            assert result == 1

            result = session.tileNames2ArrayIdx(
                self.workspace + '/', self.arrayName)
            assert result == 1

    def test_tileNames2ArrayIdx_neg_test_workspace(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            workspace = "Invalid"
            with pytest.raises(ValueError) as exec_info:
                session.tileNames2ArrayIdx(workspace, self.arrayName)
            # assert result[0] == "/home/variantdb/DB"
            assert "Invalid workspace" in str(exec_info.value)

    def test_tileNames2ArrayIdx_neg_test_array_name(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            arrayName = "Invalid"
            with pytest.raises(ValueError) as exec_info:
                session.tileNames2ArrayIdx(self.workspace, arrayName)
            # assert result[0] == "/home/variantdb/DB"
            assert "Invalid workspace" in str(exec_info.value)

    def test_arrayId2TileRows(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            idx = 1
            result = session.arrayId2TileRows(idx)
            self.typeCheck(result, list, long, self.numRows)
            assert result == range(0, self.numRows)

    def test_arrayId2TileRows_neg_test(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            idx = 2
            result = session.arrayId2TileRows(idx)
            self.typeCheck(result, list, long, 0)

    def test_contig2Tile_and_tile2contig(self):
        offset = 0
        idx = 1
        with query.DBQuery(self.DBURI).getSession() as session:
            for i in xrange(0, len(self.chromosomes)):
                contig = self.chromosomes[i]

                length = self.chromosome_lengths[contig]
                # Check at position 1 in chromosome
                contig_position = 1
                result = session.contig2Tile(idx, contig, contig_position)
                self.typeCheck(result, list, long, 1)

                if contig == 'M':
                    MT_result = session.contig2Tile(idx, 'MT', contig_position)
                    self.typeCheck(MT_result, list, long, 1)
                    assert MT_result == result

                resultContigList, resultPositionList = session.tile2Contig(
                    idx, result)
                self.typeCheck(resultContigList, list, str, 1)
                self.typeCheck(resultPositionList, list, long, 1)
                assert resultContigList[0] == contig
                assert resultPositionList[0] == contig_position

                if i == 0:
                    with pytest.raises(ValueError) as exec_info:
                        session.tile2Contig(idx, offset - 100)
                    assert "Invalid Position" in str(exec_info.value)

                if i == len(self.chromosomes) - 1:
                    with pytest.raises(ValueError) as exec_info:
                        session.tile2Contig(idx, offset + (2 * length))
                    assert "Invalid Position" in str(exec_info.value)

                offset += long(length * 1.1)

    def test_contig2Tile_neg(self):
        idx = 1
        contig_position = 1
        contig = self.chromosomes[0]
        length = self.chromosome_lengths[contig]

        with query.DBQuery(self.DBURI).getSession() as session:
            with pytest.raises(ValueError) as exec_info:
                session.contig2Tile(0, contig, contig_position)
            assert "Invalid array" in str(exec_info.value)

            with pytest.raises(ValueError) as exec_info:
                session.contig2Tile(idx, contig, (length * 2))
            assert "Invalid Query. Position" in str(exec_info.value)

            with pytest.raises(ValueError) as exec_info:
                session.contig2Tile(idx, contig, -1)
            assert "Invalid Query. Position" in str(exec_info.value)

            with pytest.raises(ValueError) as exec_info:
                session.contig2Tile(idx, "Invalid contig", contig_position)
            assert "Invalid" in str(exec_info.value)

    def test_tileRow2CallSet(self):
        idx = 1
        with query.DBQuery(self.DBURI).getSession() as session:
            for tile_row_id in range(0, self.numRows):
                result = session.tileRow2CallSet(idx, tile_row_id)
                self.typeCheck(result, list, long, 1)
                self.typeCheck(result[0], tuple, long, 4)
                assert isinstance(result[2], unicode)
                assert isinstance(result[3], unicode)
            
            result = session.tileRow2CallSet(idx, xrange(0, self.numRows))
            self.typeCheck(result, list, long, self.numRows)
            self.typeCheck(result[0], tuple, long, 4)
            assert isinstance(result[2], unicode)
            assert isinstance(result[3], unicode)

    def test_tileRow2CallSet_neg(self):
        idx = 1
        tile_row_id = self.numRows - 1
        with query.DBQuery(self.DBURI).getSession() as session:
            with pytest.raises(ValueError) as exec_info:
                session.tileRow2CallSet(-1, tile_row_id)
            assert "Invalid Array Id" in str(exec_info.value)

            with pytest.raises(ValueError) as exec_info:
                session.tileRow2CallSet(idx, self.numRows)
            assert "Invalid Array Id" in str(exec_info.value)

    def test_datasetId2VariantSets(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            result = session.datasetId2VariantSets(self.dataset_id)
            self.typeCheck(result, list, models.variant_set.VariantSet, 1)

            result = session.datasetId2VariantSets("Invalid")
            self.typeCheck(result, list, None, 0)

    def test_referenceSetIdx2ReferenceSetGUID(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            result = session.referenceSetIdx2ReferenceSetGUID(1)
            assert isinstance(result, unicode)

            with pytest.raises(ValueError) as exec_info:
                session.referenceSetIdx2ReferenceSetGUID(-1)
            assert "Invalid Reference Set Id" in str(exec_info.value)

    def test_callSetId2VariantSet(self):
        idx = 1
        tile_row_id = self.numRows - 1
        with query.DBQuery(self.DBURI).getSession() as session:
            callset = session.tileRow2CallSet(idx, tile_row_id)

            result = session.callSetId2VariantSet(callset[0])
            self.typeCheck(result, tuple, long, 2)
            assert isinstance(result[1], unicode)

            with pytest.raises(ValueError) as exec_info:
                session.callSetId2VariantSet(-1)
            assert "Invalid call set Id" in str(exec_info.value)

    def test_getArrayRows_idx(self):
        idx = 1
        with query.DBQuery(self.DBURI).getSession() as session:
            result = session.getArrayRows(array_idx=idx)
            assert isinstance(result, dict)
            self.typeCheck(result[idx], list, long, self.numRows)
            assert result[idx] == range(0, self.numRows)

            result = session.getArrayRows(array_idx=-1)
            assert isinstance(result, dict)
            assert len(result) == 0

    def test_getArrayRows_callset(self):
        idx = 1
        callset_guid = [None] * self.numRows
        with query.DBQuery(self.DBURI).getSession() as session:
            for tile_row_id in range(0, self.numRows):
                result = session.tileRow2CallSet(idx, tile_row_id)
                callset_guid[tile_row_id] = result[1]

            result = session.getArrayRows(callSets=callset_guid)
            assert isinstance(result, dict)
            self.typeCheck(result[idx], list, long, self.numRows)
            assert result[idx] == range(0, self.numRows)

            result = session.getArrayRows(callSets=["invalid"])
            assert isinstance(result, dict)
            assert len(result) == 0

    def test_getArrayRows_variantset(self):
        idx = 1
        with query.DBQuery(self.DBURI).getSession() as session:
            result = session.datasetId2VariantSets(self.dataset_id)
            vs = result[0]

            result = session.getArrayRows(variantSets=[vs.guid])
            assert isinstance(result, dict)
            self.typeCheck(result[idx], list, long, self.numRows)
            assert result[idx] == range(0, self.numRows)

            result = session.getArrayRows(variantSets=["invalid"])
            assert isinstance(result, dict)
            assert len(result) == 0

    def test_getArrayRows_combo(self):
        idx = 1
        callset_guid = [None] * self.numRows
        with query.DBQuery(self.DBURI).getSession() as session:
            for tile_row_id in range(0, self.numRows):
                result = session.tileRow2CallSet(idx, tile_row_id)
                callset_guid[tile_row_id] = result[1]

            result = session.datasetId2VariantSets(self.dataset_id)
            vs = result[0]

            result = session.getArrayRows(array_idx=idx, variantSets=[vs.guid])
            assert isinstance(result, dict)
            self.typeCheck(result[idx], list, long, self.numRows)
            assert result[idx] == range(0, self.numRows)

            result = session.getArrayRows(array_idx=idx, callSets=callset_guid)
            assert isinstance(result, dict)
            self.typeCheck(result[idx], list, long, self.numRows)
            assert result[idx] == range(0, self.numRows)

            result = session.getArrayRows(
                variantSets=[vs.guid], callSets=callset_guid)
            assert isinstance(result, dict)
            self.typeCheck(result[idx], list, long, self.numRows)
            assert result[idx] == range(0, self.numRows)

            result = session.getArrayRows(
                array_idx=idx, callSets=callset_guid, variantSets=[vs.guid])
            assert isinstance(result, dict)
            self.typeCheck(result[idx], list, long, self.numRows)
            assert result[idx] == range(0, self.numRows)

    def test_callSetIds2TileRowId(self):
        idx = 1
        callset_id = [None] * self.numRows
        callset_guid = [None] * self.numRows
        with query.DBQuery(self.DBURI).getSession() as session:
            for tile_row_id in range(0, self.numRows):
                result = session.tileRow2CallSet(idx, tile_row_id)
                callset_id[tile_row_id] = result[0]
                callset_guid[tile_row_id] = result[1]

            tile_rows_for_callset_id = session.callSetIds2TileRowId(
                callset_id, self.workspace, self.arrayName, isGUID=False)
            self.typeCheck(tile_rows_for_callset_id, list, str, self.numRows)

            tile_rows_for_callset_guid = session.callSetIds2TileRowId(
                callset_guid, self.workspace + '/', self.arrayName, isGUID=True)
            self.typeCheck(tile_rows_for_callset_guid, list, str, self.numRows)

            assert tile_rows_for_callset_id == tile_rows_for_callset_guid

            callset_id.append(-1)
            neg_tile_rows_for_callset_id = session.callSetIds2TileRowId(
                callset_id, self.workspace, self.arrayName, isGUID=False)
            self.typeCheck(neg_tile_rows_for_callset_id,
                           list, str, self.numRows)

            assert neg_tile_rows_for_callset_id == tile_rows_for_callset_id

    def test_variantSetGUID2Id(self):
        with query.DBQuery(self.DBURI).getSession() as session:
            result = session.datasetId2VariantSets(self.dataset_id)
            vs = result[0]

            result = session.variantSetGUID2Id(vs.guid)
            self.typeCheck(result, tuple, long, 2)
            assert result[0] == vs.id
            assert result[1] == vs.guid

    def test_arrayIdx2CallSets(self):
        callsets_samples = [None] * (self.numRows)
        with query.DBQuery(self.DBURI).getSession() as session:
            idx = session.tileNames2ArrayIdx(self.workspace, self.arrayName)
            for tile_row_id in range(0, self.numRows):
                s_idx = 2 * tile_row_id + 1
                callset_guid = session.tileRow2CallSet(idx, tile_row_id)[1]
                callsets_samples[tile_row_id] = (
                    callset_guid, long(s_idx), long(s_idx + 1))

            result = session.arrayIdx2CallSets(idx)
            self.typeCheck(result, list, tuple, self.numRows)
            assert set(result) == set(callsets_samples)

            with pytest.raises(ValueError) as exec_info:
                session.arrayIdx2CallSets(-1)
            assert "Invalid array id" in str(exec_info.value)

    def test_sampleIdx2SampleName(self):
        idx = 1
        with query.DBQuery(self.DBURI).getSession() as session:
            name = session.sampleIdx2SampleName(idx)
            assert isinstance(name, unicode)
            assert name == "SA245"

            with pytest.raises(ValueError) as exec_info:
                session.sampleIdx2SampleName(-1)
            assert "Invalid sample id" in str(exec_info.value)
