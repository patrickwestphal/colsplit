from nose.tools import *
import unittest

from colsplit.colsplitter import ColSplitter


class TestColSplitter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_line__line_token_update(self):
        line_1 = 'one two three'
        line_1_num_tokens = 3
        line_2 = 'one two three four'
        line_2_num_tokens = 4
        line_3 = 'one two'

        clsplttr = ColSplitter()
        clsplttr.add_line(line_1)
        self.assertEqual(line_1_num_tokens, clsplttr._max_line_tokens)

        clsplttr.add_line(line_2)
        self.assertEqual(line_2_num_tokens, clsplttr._max_line_tokens)

        clsplttr.add_line(line_3)
        self.assertEqual(line_2_num_tokens, clsplttr._max_line_tokens)

    def test_add_line__token_str_len_update(self):
        line_1 = 'aa aaaa aaa'
        line_1_max_token_len = 4
        line_2 = 'aaa aaaaaa aaaa'
        line_2_max_token_len = 6
        line_3 = 'aaaaa aaa a'

        clsplttr = ColSplitter()
        clsplttr.add_line(line_1)
        self.assertEqual(line_1_max_token_len, clsplttr._max_token_str_len)

        clsplttr.add_line(line_2)
        self.assertEqual(line_2_max_token_len, clsplttr._max_token_str_len)

        clsplttr.add_line(line_3)
        self.assertEqual(line_2_max_token_len, clsplttr._max_token_str_len)

    def test__create_array(self):
        line_1 = 'one two three'
        line_2 = 'four five six seven eight'
        line_3 = 'nine'

        num_lines = 3
        num_cols = 5

        clsplttr = ColSplitter()
        clsplttr.add_line(line_1)
        clsplttr.add_line(line_2)
        clsplttr.add_line(line_3)

        arr = clsplttr._create_array()

        arr_lines, arr_cols = arr.shape
        self.assertEqual(num_lines, arr_lines)
        self.assertEqual(num_cols, arr_cols)

        self.assertEqual(b'one', arr[0, 0])
        self.assertEqual(b'two', arr[0, 1])
        self.assertEqual(b'three', arr[0, 2])
        self.assertEqual(clsplttr._null, arr[0, 3])
        self.assertEqual(clsplttr._null, arr[0, 4])

        self.assertEqual(b'four', arr[1, 0])
        self.assertEqual(b'five', arr[1, 1])
        self.assertEqual(b'six', arr[1, 2])
        self.assertEqual(b'seven', arr[1, 3])
        self.assertEqual(b'eight', arr[1, 4])

        self.assertEqual(b'nine', arr[2, 0])
        self.assertEqual(clsplttr._null, arr[2, 1])
        self.assertEqual(clsplttr._null, arr[2, 2])
        self.assertEqual(clsplttr._null, arr[2, 3])
        self.assertEqual(clsplttr._null, arr[2, 4])

    def test__get_type(self):
        clsplttr = ColSplitter()

        null_token = clsplttr._null
        self.assertEqual(clsplttr._null_type, clsplttr._get_type(null_token))

        str_token = 'test123'
        self.assertEqual(clsplttr._str, clsplttr._get_type(str_token))

        int_token = '2345'
        self.assertEqual(clsplttr._int, clsplttr._get_type(int_token))

        int_token = '02345'
        self.assertEqual(clsplttr._int, clsplttr._get_type(int_token))

        float_token = '0.123'
        self.assertEqual(clsplttr._float, clsplttr._get_type(float_token))

    def test__hom_on_types___token_col_types_homogeneous(self):
        line_1 = '1'
        line_2 = '2'
        line_3 = '3'
        line_4 = '4'
        line_5 = '5'

        clsplttr = ColSplitter()
        clsplttr.add_line(line_1)
        clsplttr.add_line(line_2)
        clsplttr.add_line(line_3)
        clsplttr.add_line(line_4)
        clsplttr.add_line(line_5)
        clsplttr.get_data()
        self.assertEqual(1, len(clsplttr._token_col_types))
        self.assertEqual(clsplttr._int, clsplttr._token_col_types[0])

        line_6 = 'a'
        clsplttr.add_line(line_6)
        self.assertGreater(1, len(clsplttr._token_col_types))
