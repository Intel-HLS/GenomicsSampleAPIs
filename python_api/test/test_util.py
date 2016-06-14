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
