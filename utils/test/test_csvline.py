import pytest
import utils.csvline as csvline


class TestCSVLine:

    def test_init_versions(self):
        num_versions = 1
        for version in xrange(1, (num_versions + 2)):
            test_csvobj = csvline.CSVLine(version)

            if version >= num_versions:
                attribute = "invalid"
            else:
                attribute = test_csvobj.fieldNames[version][0]
            with pytest.raises(ValueError) as exec_info:
                test_csvobj.set(attribute, "any")
            assert "{0} is not a valid attribute".format(
                attribute) in str(exec_info.value)
            assert test_csvobj.get(attribute) is None

    def test_set_GT_PLOIDY(self):
        test_csvobj = csvline.CSVLine()

        assert test_csvobj.ploidy == 0
        with pytest.raises(SyntaxError) as exec_info:
            test_csvobj.set('GT', [])
        assert "PLOIDY must be set before calling set GT" in str(
            exec_info.value)

        with pytest.raises(TypeError) as exec_info:
            test_csvobj.set('GT', "value")
        assert "GT takes a list as input" in str(exec_info.value)

        for ploidy in xrange(1, 4):
            test_csvobj.set('PLOIDY', ploidy)
            assert test_csvobj.ploidy == ploidy
            assert test_csvobj.get('GT') == [csvline.EMPTYCHAR] * ploidy

            with pytest.raises(ValueError) as exec_info:
                test_csvobj.set('GT', [csvline.EMPTYCHAR] * (ploidy - 1))
            assert "GT[] must be of length" in str(exec_info.value)

            value = [1] * ploidy
            test_csvobj.set('GT', value)
            assert test_csvobj.get('GT') == value

        test_csvobj.reinit()
        assert test_csvobj.get('GT') == csvline.EMPTYCHAR

    def test_SB(self):
        test_csvobj = csvline.CSVLine()

        with pytest.raises(TypeError) as exec_info:
            test_csvobj.set('SB', "value")
        assert "SB takes a list as input" in str(exec_info.value)

        with pytest.raises(ValueError) as exec_info:
            test_csvobj.set('SB', [csvline.EMPTYCHAR] * (csvline.NUM_SB - 1))
        assert "SB must have {0} entries".format(
            csvline.NUM_SB) in str(exec_info.value)

        value = [1] * csvline.NUM_SB
        test_csvobj.set('SB', value)
        assert test_csvobj.get('SB') == value

    def test_FilterId(self):
        test_csvobj = csvline.CSVLine()

        with pytest.raises(TypeError) as exec_info:
            test_csvobj.set('FilterId', "value")
        assert "FilterId takes a list as input" in str(exec_info.value)

        value = [1] * 4
        test_csvobj.set('FilterId', value)
        assert test_csvobj.get('numFilter') == len(value)
        assert test_csvobj.get('FilterId') == value

    def test_ALT(self):
        test_csvobj = csvline.CSVLine()

        with pytest.raises(TypeError) as exec_info:
            test_csvobj.set('ALT', "value")
        assert "ALT takes a list as input" in str(exec_info.value)

        value = ['A'] * 4
        test_csvobj.set('ALT', value)
        assert test_csvobj.numALT == len(value)
        assert test_csvobj.get('ALT') == value
        assert test_csvobj.get('PL') == [
            csvline.EMPTYCHAR] * (((len(value) + 1) * (len(value) + 2)) / 2)

    def test_AD(self):
        test_csvobj = csvline.CSVLine()

        with pytest.raises(TypeError) as exec_info:
            test_csvobj.set('AD', "value")
        assert "AD takes a list as input" in str(exec_info.value)

        with pytest.raises(SyntaxError) as exec_info:
            test_csvobj.set('AD', [])
        assert "ALT must be set before calling set AD" in str(exec_info.value)

        value = ['A'] * 4
        test_csvobj.set('ALT', value)
        value = [1] * (test_csvobj.numAD - 1)
        with pytest.raises(ValueError) as exec_info:
            test_csvobj.set('AD', value)
        assert "AD[] must be of length" in str(exec_info.value)

        value = [1] * test_csvobj.numAD
        test_csvobj.set('AD', value)
        assert test_csvobj.get('AD') == value

    def test_AF(self):
        test_csvobj = csvline.CSVLine()

        with pytest.raises(TypeError) as exec_info:
            test_csvobj.set('AF', "value")
        assert "AF takes a list as input" in str(exec_info.value)

        with pytest.raises(SyntaxError) as exec_info:
            test_csvobj.set('AF', [])
        assert "ALT must be set before calling set AF" in str(exec_info.value)

        value = ['A'] * 4
        test_csvobj.set('ALT', value)
        value = [1] * (test_csvobj.numALT - 1)
        with pytest.raises(ValueError) as exec_info:
            test_csvobj.set('AF', value)
        assert "AF[] must be of length" in str(exec_info.value)

        value = [1] * test_csvobj.numALT
        test_csvobj.set('AF', value)
        assert test_csvobj.get('AF') == value

    def test_AC(self):
        test_csvobj = csvline.CSVLine()

        with pytest.raises(TypeError) as exec_info:
            test_csvobj.set('AC', "value")
        assert "AC takes a list as input" in str(exec_info.value)

        with pytest.raises(SyntaxError) as exec_info:
            test_csvobj.set('AC', [])
        assert "ALT must be set before calling set AC" in str(exec_info.value)

        value = ['A'] * 4
        test_csvobj.set('ALT', value)
        value = [1] * (test_csvobj.numALT - 1)
        with pytest.raises(ValueError) as exec_info:
            test_csvobj.set('AC', value)
        assert "AC[] must be of length" in str(exec_info.value)

        value = [1] * test_csvobj.numALT
        test_csvobj.set('AC', value)
        assert test_csvobj.get('AC') == value

    def test_PL(self):
        test_csvobj = csvline.CSVLine()

        with pytest.raises(TypeError) as exec_info:
            test_csvobj.set('PL', "value")
        assert "PL takes a list as input" in str(exec_info.value)

        with pytest.raises(SyntaxError) as exec_info:
            test_csvobj.set('PL', [])
        assert "ALT must be set before calling set PL" in str(exec_info.value)

        value = ['A'] * 4
        test_csvobj.set('ALT', value)
        value = [1] * (test_csvobj.numPL - 1)
        with pytest.raises(ValueError) as exec_info:
            test_csvobj.set('PL', value)
        assert "PL[] must be of length" in str(exec_info.value)

        value = [1] * test_csvobj.numPL
        test_csvobj.set('PL', value)
        assert test_csvobj.get('PL') == value

    def test_runChecks(self):
        test_csvobj = csvline.CSVLine()

        # No SampleId was set
        result = test_csvobj.runChecks()
        assert result[0] == False
        assert "SampleId" in result[1] and "is invalid" in result[1]
        assert "Location" in result[1]
        assert "End" in result[1]
        assert "ALT must be set" in result[1]

        test_csvobj.set('SampleId', -1)
        result = test_csvobj.runChecks()
        assert result[0] == False
        assert "SampleId" in result[1] and "is invalid" in result[1]

        test_csvobj.set('SampleId', 1)
        result = test_csvobj.runChecks()
        assert "SampleId" not in result[1]
        assert "Location" in result[1] and "is invalid" in result[1]
        assert result[0] == False

        test_csvobj.set('Location', -1)
        result = test_csvobj.runChecks()
        assert result[0] == False
        assert "Location" in result[1] and "is invalid" in result[1]

        test_csvobj.set('Location', 100)
        result = test_csvobj.runChecks()
        assert "Location" not in result[1]
        assert "End" in result[1] and "is invalid" in result[1]
        assert result[0] == False

        test_csvobj.set('End', -1)
        result = test_csvobj.runChecks()
        assert result[0] == False
        assert "End" in result[1] and "is invalid" in result[1]

        test_csvobj.set('End', 1)
        result = test_csvobj.runChecks()
        assert result[0] == False
        assert "End" in result[1] and "< Start" in result[1]

        test_csvobj.set('End', 100)
        result = test_csvobj.runChecks()
        assert "End" not in result[1]
        assert "ALT must be set" in result[1]
        assert result[0] == False

        test_csvobj.set('ALT', ['A'])
        result = test_csvobj.runChecks()
        assert "Failed" not in result[1]
        assert result[0] == True

    def test_getCSVLine(self):
        test_csvobj = csvline.CSVLine()

        result = test_csvobj.getCSVLine()
        assert "failed" in result

        # Update to avoid run check failure
        test_csvobj.set('SampleId', 1)
        test_csvobj.set('Location', 100)
        test_csvobj.set('End', 100)
        test_csvobj.set('ALT', ['A'])
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,*,A,*,0,*,*,*,*,*,*,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('REF', 'T')
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,*,0,*,*,*,*,*,*,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('QUAL', 5.45)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,0,*,*,*,*,*,*,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('FilterId', [1, 2])
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,*,*,*,*,*,*,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('BaseQRankSum', 35.7)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,*,*,*,*,*,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('ClippingRankSum', 5.7)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,*,*,*,*,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('MQRankSum', 15.7)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,*,*,*,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('ReadPosRankSum', 17.7)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,*,*,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('MQ', 8.5)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,*,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('MQ0', 9)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('AF', [3.14])
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('AN', 100)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('AC', [90])
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('DP', 7)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('DP_FMT', 2)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('MIN_DP', 1)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,*,*,*,*,*,0,0,*,*"
        test_csvobj.set('GQ', 10)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,*,*,*,*,0,0,*,*"
        test_csvobj.set('SB', range(21, 25))
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,21,22,23,24,0,0,*,*"
        test_csvobj.set('AD', range(25, 27))
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,21,22,23,24,2,25,26,0,*,*"
        test_csvobj.set('PL', range(70, 73))
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,21,22,23,24,2,25,26,3,70,71,72,*,*"
        test_csvobj.set('PLOIDY', 2)
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,21,22,23,24,2,25,26,3,70,71,72,2,*,*,*"
        test_csvobj.set('GT', [1, 2])
        assert test_csvobj.getCSVLine(
            clear=False) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,21,22,23,24,2,25,26,3,70,71,72,2,1,2,*"
        test_csvobj.set('PS', 12345)
        assert test_csvobj.getCSVLine(
            clear=True) == "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,21,22,23,24,2,25,26,3,70,71,72,2,1,2,12345"

        assert test_csvobj.numALT == 0

    def test_invalidate(self):
        errorString = "Test invalidate"
        test_csvobj = csvline.CSVLine()
        assert test_csvobj.isValid == True
        test_csvobj.invalidate(errorString)
        assert test_csvobj.isValid == False
        assert test_csvobj.error == errorString

    def test_loadCSV(self):
        test_csvobj = csvline.CSVLine()
        csv = "1,100,100,*,A,*,0,*,*,*,*,*,*,0,*,0,*,*,*,*,*,*,*,*,0,0,*,*"
        test_csvobj.loadCSV(csv)
        assert test_csvobj.get('SampleId') == '1'
        assert test_csvobj.get('Location') == '100'
        assert test_csvobj.get('End') == '100'
        assert test_csvobj.get('ALT') == ['A']
        assert test_csvobj.get('REF') == '*'
        assert test_csvobj.get('QUAL') == '*'
        assert test_csvobj.get('FilterId') == []
        assert test_csvobj.get('BaseQRankSum') == '*'
        assert test_csvobj.get('ClippingRankSum') == '*'
        assert test_csvobj.get('MQRankSum') == '*'
        assert test_csvobj.get('ReadPosRankSum') == '*'
        assert test_csvobj.get('DP') == '*'
        assert test_csvobj.get('MQ') == '*'
        assert test_csvobj.get('MQ0') == '*'
        assert test_csvobj.get('DP_FMT') == '*'
        assert test_csvobj.get('MIN_DP') == '*'
        assert test_csvobj.get('GQ') == '*'
        assert test_csvobj.get('SB') == ['*', '*', '*', '*']
        assert test_csvobj.get('AD') == ['*', '*']
        assert test_csvobj.get('PL') == ['*', '*', '*']
        assert test_csvobj.get('AF') == ['*']
        assert test_csvobj.get('AN') == '*'
        assert test_csvobj.get('AC') == ['*']
        assert test_csvobj.get('PLOIDY') == 0
        assert test_csvobj.get('GT') == []
        assert test_csvobj.get('PS') == '*'
        assert test_csvobj.getCSVLine(True) == csv

        csv = "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,21,22,23,24,0,0,*,*"
        test_csvobj.loadCSV(csv)
        assert test_csvobj.get('SampleId') == '1'
        assert test_csvobj.get('Location') == '100'
        assert test_csvobj.get('End') == '100'
        assert test_csvobj.get('ALT') == ['A']
        assert test_csvobj.get('REF') == 'T'
        assert test_csvobj.get('QUAL') == '5.45'
        assert test_csvobj.get('FilterId') == ['1', '2']
        assert test_csvobj.get('BaseQRankSum') == '35.7'
        assert test_csvobj.get('ClippingRankSum') == '5.7'
        assert test_csvobj.get('MQRankSum') == '15.7'
        assert test_csvobj.get('ReadPosRankSum') == '17.7'
        assert test_csvobj.get('DP') == '7'
        assert test_csvobj.get('MQ') == '8.5'
        assert test_csvobj.get('MQ0') == '9'
        assert test_csvobj.get('DP_FMT') == '2'
        assert test_csvobj.get('MIN_DP') == '1'
        assert test_csvobj.get('GQ') == '10'
        assert test_csvobj.get('SB') == ['21', '22', '23', '24']
        assert test_csvobj.get('AD') == ['*', '*']
        assert test_csvobj.get('PL') == ['*', '*', '*']
        assert test_csvobj.get('AF') == ['3.14']
        assert test_csvobj.get('AN') == '100'
        assert test_csvobj.get('AC') == ['90']
        assert test_csvobj.get('PLOIDY') == 0
        assert test_csvobj.get('GT') == []
        assert test_csvobj.get('PS') == '*'
        assert test_csvobj.getCSVLine(True) == csv

        csv = "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,21,22,23,24,2,25,26,3,70,71,72,*,*"
        test_csvobj.loadCSV(csv)
        assert test_csvobj.get('SampleId') == '1'
        assert test_csvobj.get('Location') == '100'
        assert test_csvobj.get('End') == '100'
        assert test_csvobj.get('ALT') == ['A']
        assert test_csvobj.get('REF') == 'T'
        assert test_csvobj.get('QUAL') == '5.45'
        assert test_csvobj.get('FilterId') == ['1', '2']
        assert test_csvobj.get('BaseQRankSum') == '35.7'
        assert test_csvobj.get('ClippingRankSum') == '5.7'
        assert test_csvobj.get('MQRankSum') == '15.7'
        assert test_csvobj.get('ReadPosRankSum') == '17.7'
        assert test_csvobj.get('DP') == '7'
        assert test_csvobj.get('MQ') == '8.5'
        assert test_csvobj.get('MQ0') == '9'
        assert test_csvobj.get('DP_FMT') == '2'
        assert test_csvobj.get('MIN_DP') == '1'
        assert test_csvobj.get('GQ') == '10'
        assert test_csvobj.get('SB') == ['21', '22', '23', '24']
        assert test_csvobj.get('AD') == ['25', '26']
        assert test_csvobj.get('PL') == ['70', '71', '72']
        assert test_csvobj.get('AF') == ['3.14']
        assert test_csvobj.get('AN') == '100'
        assert test_csvobj.get('AC') == ['90']
        assert test_csvobj.get('PLOIDY') == 0
        assert test_csvobj.get('GT') == []
        assert test_csvobj.get('PS') == '*'
        assert test_csvobj.getCSVLine(True) == csv

        csv = "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,21,22,23,24,2,25,26,3,70,71,72,2,1,2,*"
        test_csvobj.loadCSV(csv)
        assert test_csvobj.get('SampleId') == '1'
        assert test_csvobj.get('Location') == '100'
        assert test_csvobj.get('End') == '100'
        assert test_csvobj.get('ALT') == ['A']
        assert test_csvobj.get('REF') == 'T'
        assert test_csvobj.get('QUAL') == '5.45'
        assert test_csvobj.get('FilterId') == ['1', '2']
        assert test_csvobj.get('BaseQRankSum') == '35.7'
        assert test_csvobj.get('ClippingRankSum') == '5.7'
        assert test_csvobj.get('MQRankSum') == '15.7'
        assert test_csvobj.get('ReadPosRankSum') == '17.7'
        assert test_csvobj.get('DP') == '7'
        assert test_csvobj.get('MQ') == '8.5'
        assert test_csvobj.get('MQ0') == '9'
        assert test_csvobj.get('DP_FMT') == '2'
        assert test_csvobj.get('MIN_DP') == '1'
        assert test_csvobj.get('GQ') == '10'
        assert test_csvobj.get('SB') == ['21', '22', '23', '24']
        assert test_csvobj.get('AD') == ['25', '26']
        assert test_csvobj.get('PL') == ['70', '71', '72']
        assert test_csvobj.get('AF') == ['3.14']
        assert test_csvobj.get('AN') == '100'
        assert test_csvobj.get('AC') == ['90']
        assert test_csvobj.get('PLOIDY') == 2
        assert test_csvobj.get('GT') == ['1', '2']
        assert test_csvobj.get('PS') == '*'
        assert test_csvobj.getCSVLine(True) == csv

        csv = "1,100,100,T,A,5.45,2,1,2,35.7,5.7,15.7,17.7,8.5,9,1,3.14,100,1,90,7,2,1,10,21,22,23,24,2,25,26,3,70,71,72,2,1,2,12345"
        test_csvobj.loadCSV(csv)
        assert test_csvobj.get('SampleId') == '1'
        assert test_csvobj.get('Location') == '100'
        assert test_csvobj.get('End') == '100'
        assert test_csvobj.get('ALT') == ['A']
        assert test_csvobj.get('REF') == 'T'
        assert test_csvobj.get('QUAL') == '5.45'
        assert test_csvobj.get('FilterId') == ['1', '2']
        assert test_csvobj.get('BaseQRankSum') == '35.7'
        assert test_csvobj.get('ClippingRankSum') == '5.7'
        assert test_csvobj.get('MQRankSum') == '15.7'
        assert test_csvobj.get('ReadPosRankSum') == '17.7'
        assert test_csvobj.get('DP') == '7'
        assert test_csvobj.get('MQ') == '8.5'
        assert test_csvobj.get('MQ0') == '9'
        assert test_csvobj.get('DP_FMT') == '2'
        assert test_csvobj.get('MIN_DP') == '1'
        assert test_csvobj.get('GQ') == '10'
        assert test_csvobj.get('SB') == ['21', '22', '23', '24']
        assert test_csvobj.get('AD') == ['25', '26']
        assert test_csvobj.get('PL') == ['70', '71', '72']
        assert test_csvobj.get('AF') == ['3.14']
        assert test_csvobj.get('AN') == '100'
        assert test_csvobj.get('AC') == ['90']
        assert test_csvobj.get('PLOIDY') == 2
        assert test_csvobj.get('GT') == ['1', '2']
        assert test_csvobj.get('PS') == '12345'
        assert test_csvobj.getCSVLine(True) == csv
