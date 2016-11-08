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
from unittest import TestCase
import utils.helper as helper

class TestReferenceFasta(TestCase):

    @classmethod
    def setUpClass(self):
        self.fasta = """>chr1
NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNA
CTGNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN
>chrM
GANN
"""

    @pytest.fixture(autouse=True)
    def set_tmpdir(self, tmpdir):
        self.tmpdir = tmpdir

    def test_getReference(self):
        fastafile = self.tmpdir.join('test.fasta')
        fastafile.write(self.fasta)
        assert helper.verifyFasta(str(fastafile)) is None
        assert helper.getReference("GRCh37", "1", 100, 101, str(fastafile)) != ""
        assert helper.getReference("GRCh37", "M", 1, 2, str(fastafile)) == "GA"
        assert helper.getReference("GRCh37", "MT", 1, 2, str(fastafile)) == "GA"
    
    def test_getReference_neg(self):
        with pytest.raises(Exception) as exec_info:
            helper.getReference("GRCh37", "1", 100, 101, '/tmp/missing.fasta')
        assert 'is invalid' in str(exec_info.value)
        
    def test_verifyFasta_neg(self):
        fastafile = self.tmpdir.join('test_neg.fasta')
        with pytest.raises(Exception) as exec_info:
            helper.verifyFasta(str(fastafile))
        assert 'is invalid' in str(exec_info.value)

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
