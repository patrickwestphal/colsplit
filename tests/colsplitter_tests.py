import unittest

import numpy as np
from nose.tools import *

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
        clsplttr.get_data()
        self.assertGreater(len(clsplttr._token_col_types), 1)

    def test__move_from_null_col(self):
        cs = ColSplitter()
        cs._token_col_types = [cs._int]
        cs._max_token_str_len = 6
        cs._line_counter = 6
        arr = np.chararray((6, 3), cs._max_token_str_len)
        # 0) left: OK
        arr[0] = [cs._null, '23', 'test01']
        # 1) left: wrong type; right: NULL
        arr[1] = [cs._null, 'test02', cs._null]
        # 2) left: wrong type; right: not NULL
        arr[2] = [cs._null, 'test03', 'test04']
        # 3) left: already assigned; right: NULL
        arr[3] = ['24', 'test05', cs._null]
        # 4) left: already assigned; right not NULL
        arr[4] = ['25', 'test06', 'test07']
        # 5) not to move
        arr[5] = ['26', cs._null, 'test08']
        arr = cs._move_from_null_col(arr, 1, cs._int, cs._valid)

        self.assertEqual((6, 3), arr.shape)
        # 0)
        self.assertEqual(b'23', arr[0, 0])
        self.assertEqual(b'test01', arr[0, 1])
        self.assertEqual(cs._null, arr[0, 2])
        # 1)
        self.assertEqual(cs._null, arr[1, 0])
        self.assertEqual(b'test02', arr[1, 1])
        self.assertEqual(cs._null, arr[1, 2])
        # 2)
        self.assertEqual(cs._null, arr[2, 0])
        self.assertEqual(b'test03', arr[2, 1])
        self.assertEqual(b'test04', arr[2, 2])
        # 3)
        self.assertEqual(b'24', arr[3, 0])
        self.assertEqual(b'test05', arr[3, 1])
        self.assertEqual(cs._null, arr[3, 2])
        # 4)
        self.assertEqual(b'25', arr[4, 0])
        self.assertEqual(b'test06', arr[4, 1])
        self.assertEqual(b'test07', arr[4, 2])
        # 5)
        self.assertEqual(b'26', arr[5, 0])
        self.assertEqual(b'test08', arr[5, 1])
        self.assertEqual(cs._null, arr[5, 2])

        # in the last column
        arr = cs._move_from_null_col(arr, 2, cs._str, cs._invalid)
        self.assertEqual((6, 3), arr.shape)
        # 0)
        self.assertEqual(b'23', arr[0, 0])
        self.assertEqual(b'test01', arr[0, 1])
        self.assertEqual(cs._null, arr[0, 2])
        # 1)
        self.assertEqual(cs._null, arr[1, 0])
        self.assertEqual(b'test02', arr[1, 1])
        self.assertEqual(cs._null, arr[1, 2])
        # 2)
        self.assertEqual(cs._null, arr[2, 0])
        self.assertEqual(b'test03', arr[2, 1])
        self.assertEqual(b'test04', arr[2, 2])
        # 3)
        self.assertEqual(b'24', arr[3, 0])
        self.assertEqual(b'test05', arr[3, 1])
        self.assertEqual(cs._null, arr[3, 2])
        # 4)
        self.assertEqual(b'25', arr[4, 0])
        self.assertEqual(b'test06', arr[4, 1])
        self.assertEqual(b'test07', arr[4, 2])
        # 5)
        self.assertEqual(b'26', arr[5, 0])
        self.assertEqual(b'test08', arr[5, 1])
        self.assertEqual(cs._null, arr[5, 2])

    def test__move_from_col(self):
        cs = ColSplitter()
        cs._token_col_types = [cs._int, cs._float]
        cs._max_token_str_len = 6
        cs._line_counter = 6
        arr = np.chararray((6, 3), cs._max_token_str_len)
        # 0) left: OK
        arr[0] = [cs._null, '23', 'test01']
        # 1) left: wrong type; right: NULL
        arr[1] = [cs._null, 'test02', cs._null]
        # 2) left: wrong type; right: not NULL
        arr[2] = [cs._null, 'test03', 'test04']
        # 3) left: already assigned; right: NULL
        arr[3] = ['24', '25', cs._null]
        # 4) left: already assigned; right not NULL
        arr[4] = ['26', '27', 'test05']
        # 5) not to move
        arr[5] = [cs._null, '0.5', cs._null]
        arr = cs._move_from_col(arr, 1, cs._float, cs._int, cs._valid)

        self.assertEqual((6, 4), arr.shape)
        # 0)
        self.assertEqual(b'23', arr[0, 0])
        self.assertEqual(cs._null, arr[0, 1])
        self.assertEqual(b'test01', arr[0, 2])
        self.assertEqual(cs._null, arr[0, 3])
        # 1)
        self.assertEqual(cs._null, arr[1, 0])
        self.assertEqual(cs._null, arr[1, 1])
        self.assertEqual(b'test02', arr[1, 2])
        self.assertEqual(cs._null, arr[1, 3])
        # 2)
        self.assertEqual(cs._null, arr[2, 0])
        self.assertEqual(cs._null, arr[2, 1])
        self.assertEqual(b'test03', arr[2, 2])
        self.assertEqual(b'test04', arr[2, 3])
        # 3)
        self.assertEqual(b'24', arr[3, 0])
        self.assertEqual(cs._null, arr[3, 1])
        self.assertEqual(b'25', arr[3, 2])
        self.assertEqual(cs._null, arr[3, 3])
        # 4)
        self.assertEqual(b'26', arr[4, 0])
        self.assertEqual(cs._null, arr[4, 1])
        self.assertEqual(b'27', arr[4, 2])
        self.assertEqual(b'test05', arr[4, 3])
        # 5)
        self.assertEqual(cs._null, arr[5, 0])
        self.assertEqual(b'0.5', arr[5, 1])
        self.assertEqual(cs._null, arr[5, 2])
        self.assertEqual(cs._null, arr[5, 3])
