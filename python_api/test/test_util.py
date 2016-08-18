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
import python_api.util as util


class TestUtil:

    def test_flattenStartEnd_simple(self):
        result = util.flattenStartEnd([1, 10, 20], [5, 15, 25])
        assert result[0] == [1, 10, 20]
        assert result[1] == [5, 15, 25]

        result = util.flattenStartEnd([10, 1, 20], [15, 5, 25])
        assert result[0] == [1, 10, 20]
        assert result[1] == [5, 15, 25]

        result = util.flattenStartEnd([20, 10, 1], [25, 15, 5])
        assert result[0] == [1, 10, 20]
        assert result[1] == [5, 15, 25]

    def test_flattenStartEnd_overlapping(self):
        result = util.flattenStartEnd([1, 10, 20], [10, 15, 25])
        assert result[0] == [1, 20]
        assert result[1] == [15, 25]

        result = util.flattenStartEnd([10, 1, 20], [15, 10, 25])
        assert result[0] == [1, 20]
        assert result[1] == [15, 25]

        result = util.flattenStartEnd([20, 10, 1], [25, 15, 10])
        assert result[0] == [1, 20]
        assert result[1] == [15, 25]

        result = util.flattenStartEnd([1, 10, 20], [15, 21, 25])
        assert result[0] == [1]
        assert result[1] == [25]

    def test_flattenStartEnd_1less(self):
        result = util.flattenStartEnd([1, 10, 20], [9, 15, 25])
        assert result[0] == [1, 20]
        assert result[1] == [15, 25]

        result = util.flattenStartEnd([1, 7, 10, 20], [6, 9, 15, 25])
        assert result[0] == [1, 20]
        assert result[1] == [15, 25]

        result = util.flattenStartEnd([20, 7, 10, 1], [25, 9, 15, 6])
        assert result[0] == [1, 20]
        assert result[1] == [15, 25]

    def test_flattenStartEnd_insertEnd(self):
        result = util.flattenStartEnd([20, 7, 10, 1], [25, 9, 15, 30])
        assert result[0] == [1]
        assert result[1] == [30]

        result = util.flattenStartEnd([20, 7, 10, 1], [25, 9, 15, 16])
        assert result[0] == [1, 20]
        assert result[1] == [16, 25]
