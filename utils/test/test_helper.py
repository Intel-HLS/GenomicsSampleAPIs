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
