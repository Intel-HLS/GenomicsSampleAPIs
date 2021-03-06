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
import unittest
import os
import sys
import json
import utils.configuration as configuration

config_path = os.path.join(os.path.realpath(
    sys.argv[-1]), "utils/example_configs/icgc_config.json")


class TestConfigReader(unittest.TestCase):

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

    def test_config_default(self):
        config = configuration.ConfigReader(config_path)

        with open(config_path, 'r') as fp:
            config_json = json.load(fp)
        assert config.HeaderStartsWith == config_json["HeaderStartsWith"]
        assert isinstance(config.VariantNameMap, list)
        assert len(config.VariantNameMap) == 5
        assert isinstance(config.CallSetIdMap, list)
        assert len(config.CallSetIdMap) == 2
        assert isinstance(config.PositionMap, dict)
        assert len(config.PositionMap) == 4
        assert isinstance(config.PositionMap["assembly"], list)
        assert len(config.PositionMap["assembly"]) == 2

        config_json['TileDBSchema']['workspace'] = "test/workspace/"
        temp_file = self.tmpdir.join('config_default.json')
        temp_file.write(json.dumps(config_json))
        config = configuration.ConfigReader(str(temp_file))

        assert config.TileDBSchema['workspace'] == "test/workspace"

    def test_getDictValue(self):
        test_dict = {"key0": 1}

        assert configuration.getDictValue(test_dict, "key0") == 1

        with pytest.raises(ValueError) as exec_info:
            configuration.getDictValue(test_dict, "key1")
        assert "is a required field" in str(exec_info.value)
