from unittest import TestCase

from power_dialer.services import _generate_line_number, _generate_central_office_code, _generateNPA

# Test by sampling 10% of the space


class Test_generateNPA(TestCase):

    def is_valid_NPA(self, npa: str) -> bool:
        """
        Validate an npa

        :param npa: Numbering plan area code
        :return: True if it's valid
        """
        return (len(npa) == 3 and
                '2' <= npa[0] <= '9' and
                '0' <= npa[1] <= '9' and
                '0' <= npa[2] <= '9'
                )

    def test_generateNPA(self):
        npas = (_generateNPA() for _ in range(100))
        assert all(self.is_valid_NPA(npa) for npa in npas)


class Test_generateCentralOfficeCode(TestCase):

    def is_valid_COC(self, coc: str) -> bool:
        """
        Validate a central office code
        :param coc: Central office code
        :return: True if it's valid
        """
        return ( len(coc) == 3 and
                 '2' <= coc[0] <= '9' and
                 '0' <= coc[1] <= '9' and
                 '0' <= coc[2] <= '9' and
                 not coc.endswith('11'))

    def test_generateCOC(self):
        npas = (_generate_central_office_code() for _ in range(100))
        assert all(self.is_valid_COC(npa) for npa in npas)


class Test_generateLineNumber(TestCase):
    def test_generate_line_number(self):
        assert all(len(_generate_line_number()) == 4 for _ in range(1000))
