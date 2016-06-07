import pytest, unittest, os, sys, json
import utils.configuration as configuration

config_path = os.path.join(os.path.realpath(sys.argv[-1]), "utils/example_configs/icgc_config.json")
class TestConfigReader(unittest.TestCase):
  @classmethod
  def setUpClass(self):
    with open(config_path, 'r') as readFP:
      config_json = json.load(readFP)
      config_json["TileDBConfig"] = os.path.join(os.path.realpath(sys.argv[-1]), "utils/example_configs/tiledb_config.json")
      config_json["TileDBAssembly"] = os.path.join(os.path.realpath(sys.argv[-1]), "utils/example_configs/hg19.json")
      config_json["VariantSetMap"]["VariantConfig"] = os.path.join(os.path.realpath(sys.argv[-1]), "utils/example_configs/icgc_variants.json")
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
