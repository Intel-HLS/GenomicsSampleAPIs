import pytest
import json
import os
from mock import patch
import python_api.config as config
from python_api.mpi_service import Aggregator

stub_result = "{\"indices\" : [0, 1], \"POSITION\": [100, 90], \"END\": [105, 105], \"REF\":[\"A\", \"T\"]}"


class TestAggregator():

    def get_test_config(self, tmpdir):
        callset_file = tmpdir.mkdir("python_api_test").join("callset.json")
        callset_file.write(
            "{\"callsets\": {\"testSample1\" : {\"row_idx\": 0}, \"testSample2\" : {\"row_idx\": 1}}}")
        loader_file = tmpdir.join("python_api_test").join("loader.json")
        loader_file.write(json.dumps(
            dict({"callset_mapping_file": str(callset_file)})))
        config.MPIConfig.ID_MAPPING = str(loader_file)
        config.MPIConfig.TEMP_DIR = str(tmpdir.join("python_api_test"))
        return config

    def test_init(self, tmpdir):
        callset_file = tmpdir.mkdir(
            "python_api_test").join("callset_basic.json")
        callset_file.write(
            "{\"callsets\": {\"testSample0\" : {\"row_idx\": 0}, \"testSample1\" : {\"row_idx\": 1}, \"testSample2\" : {\"row_idx\": 2}}}")
        loader_file = tmpdir.join("python_api_test").join("loader_simple.json")
        loader_file.write(json.dumps(
            dict({"callset_mapping_file": str(callset_file)})))
        config.MPIConfig.ID_MAPPING = str(loader_file)

        api = Aggregator(config)
        assert api.numSamples == 3
        assert api.getNumSamples() == 3
        assert api.sampleId2Name == dict(
            {0: 'testSample0', 1: 'testSample1', 2: 'testSample2'})

        vid_mapping_file = tmpdir.join("python_api_test").join("vid.json")
        vid_mapping_file.write(json.dumps(
            dict({"callset_mapping_file": str(callset_file)})))
        loader_file = tmpdir.join("python_api_test").join("loader_vid.json")
        loader_dict = dict()
        loader_dict["vid_mapping_file"] = str(vid_mapping_file)
        loader_dict["limit_callset_row_idx"] = 1
        loader_file.write(json.dumps(loader_dict))
        config.MPIConfig.ID_MAPPING = str(loader_file)

        api = Aggregator(config)
        assert api.numSamples == 2
        assert api.getNumSamples() == 2
        assert api.sampleId2Name == dict({0: 'testSample0', 1: 'testSample1'})

    def test_sample_names(self, tmpdir):
        api = Aggregator(self.get_test_config(tmpdir))

        assert api.getSampleNames(range(0, 3)) == [
            'testSample1', 'testSample2', None]
        assert api.getSampleNames([1, 2, 0]) == [
            'testSample2', None, 'testSample1']

    @patch('python_api.mpi_service.Aggregator.runMPI', return_value=stub_result)
    def test_getPosition_single(self, runMPI_patch, tmpdir):
        self.get_test_config(tmpdir)
        config.util.DEBUG = True
        api = Aggregator(config)

        result = api.getPosition("1", 100L, ["REF"])

        args, kwargs = runMPI_patch.call_args
        assert result == stub_result
        assert args[1] == "Cotton-JSON"
        with open(args[0], 'r') as fp:
            created_json = json.load(fp)
            assert created_json["query_attributes"] == ["REF"]
            assert len(created_json["query_column_ranges"]) == 1
            assert len(created_json["query_column_ranges"][0]) == 1
            assert isinstance(created_json["query_column_ranges"][0][0], dict)
            assert len(created_json["query_column_ranges"][0][0]) == 1
            assert created_json["query_column_ranges"][
                0][0] == dict({"1": 100})

        config.util.DEBUG = False
        result = api.getPosition("1", 100L, ["REF"])
        args, kwargs = runMPI_patch.call_args
        assert os.path.exists(args[0]) == False

    @patch('python_api.mpi_service.Aggregator.runMPI', return_value=stub_result)
    def test_getPosition_multi(self, runMPI_patch, tmpdir):
        self.get_test_config(tmpdir)
        config.util.DEBUG = True
        api = Aggregator(config)

        result = api.getPosition(["1", "1"], [100L, 200L], [
                                 "REF", "END", "POSITION"])

        args, kwargs = runMPI_patch.call_args
        assert result == stub_result
        assert args[1] == "Positions-JSON"
        with open(args[0], 'r') as fp:
            created_json = json.load(fp)
            assert created_json["query_attributes"] == ["REF"]
            assert len(created_json["query_column_ranges"]) == 1
            assert len(created_json["query_column_ranges"][0]) == 2
            assert isinstance(created_json["query_column_ranges"][0][0], dict)
            assert isinstance(created_json["query_column_ranges"][0][1], dict)
            assert len(created_json["query_column_ranges"][0][0]) == 1
            assert created_json["query_column_ranges"][
                0][0] == dict({"1": 100})
            assert created_json["query_column_ranges"][
                0][1] == dict({"1": 200})

        with pytest.raises(ValueError) as exec_info:
            api.getPosition(["1"], [100L, 200L], ["REF"])
        assert "!= len" in str(exec_info.value)

    @patch('python_api.mpi_service.Aggregator.runMPI', return_value=stub_result)
    def test_getPositionRange_single(self, runMPI_patch, tmpdir):
        self.get_test_config(tmpdir)
        config.util.DEBUG = True
        api = Aggregator(config)

        result = api.getPositionRange("1", 100L, 110L, ["REF"])

        args, kwargs = runMPI_patch.call_args
        assert result == stub_result
        assert args[1] == "Cotton-JSON"
        with open(args[0], 'r') as fp:
            created_json = json.load(fp)
            assert created_json["query_attributes"] == ["REF"]
            assert len(created_json["query_column_ranges"]) == 1
            assert len(created_json["query_column_ranges"][0]) == 1
            assert isinstance(created_json["query_column_ranges"][0][0], dict)
            assert len(created_json["query_column_ranges"][0][0]) == 1
            assert created_json["query_column_ranges"][
                0][0] == dict({"1": [100, 110]})

        config.util.DEBUG = False
        result = api.getPositionRange("1", 100L, 110L, ["REF"])
        args, kwargs = runMPI_patch.call_args
        assert os.path.exists(args[0]) == False

    @patch('python_api.mpi_service.Aggregator.runMPI', return_value=stub_result)
    def test_getPositionRange_multi(self, runMPI_patch, tmpdir):
        self.get_test_config(tmpdir)
        config.util.DEBUG = True
        api = Aggregator(config)

        result = api.getPositionRange(["1", "1"], [100L, 200L], [
                                      110L, 220L], ["REF", "END", "POSITION"])

        args, kwargs = runMPI_patch.call_args
        assert result == stub_result
        assert args[1] == "Positions-JSON"
        with open(args[0], 'r') as fp:
            created_json = json.load(fp)
            assert created_json["query_attributes"] == ["REF"]
            assert len(created_json["query_column_ranges"]) == 1
            assert len(created_json["query_column_ranges"][0]) == 2
            assert isinstance(created_json["query_column_ranges"][0][0], dict)
            assert isinstance(created_json["query_column_ranges"][0][1], dict)
            assert len(created_json["query_column_ranges"][0][0]) == 1
            assert created_json["query_column_ranges"][
                0][0] == dict({"1": [100, 110]})
            assert created_json["query_column_ranges"][
                0][1] == dict({"1": [200, 220]})

        with pytest.raises(ValueError) as exec_info:
            api.getPositionRange(["1"], [100L, 200L], [110L, 220L], ["REF"])
        assert "len(end)" in str(exec_info.value)

    @patch('python_api.mpi_service.Aggregator.runMPI', return_value=stub_result)
    def test_getValidPositions(self, runMPI_patch, tmpdir):
        self.get_test_config(tmpdir)
        config.util.DEBUG = True
        api = Aggregator(config)

        result = json.loads(api.getValidPositions("1", 100L, ["REF"]))
        assert len(result) == 3
        assert result["POSITION"] == [90]
        assert result["END"] == [105]
