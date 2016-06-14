import pytest
import gzip
from mock import patch
import utils.helper as helper


def test_getReference():
    assert helper.getReference("GRCh37", "1", 100, 101) != ""
    assert helper.getReference("GRCh37", "M", 1, 2) == "GA"


def raiseException():
    raise Exception("Test")


@patch('requests.get', side_effect=raiseException)
@patch('utils.helper.NUM_RETRIES', 2)
def test_getReference_neg(patched_fn):
    with pytest.raises(Exception) as exec_info:
        helper.getReference("GRCh37", "1", 100, 101)
    assert patched_fn.call_count == 2


def test_printers():
    helper.log("test")
    helper.progressPrint("test")


def test_getFileName():
    assert helper.getFileName("/tmp/test/") == ""
    assert helper.getFileName("/tmp/test/file") == "file"
    assert helper.getFileName("/tmp/test/file.ext") == "file"
    assert helper.getFileName("/tmp/test/file.ext.ext2") == "file"
    assert helper.getFileName("/tmp/test/file_ext_", splitStr="_") == "file"


class TestGetFilePointer():

    def test_getFilePointer(self, tmpdir):
        test_file = tmpdir.join("notzipped.txt")
        fp = helper.getFilePointer(str(test_file), True, 'w')
        assert isinstance(fp, gzip.GzipFile)
        fp.close()

    def test_getFilePointer_gzip(self, tmpdir):
        test_file = tmpdir.join("zipped.gz")
        fp = helper.getFilePointer(str(test_file), False, 'w')
        assert isinstance(fp, file)
        fp.close()
