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

        str_token = b'test123'
        self.assertEqual(clsplttr._str, clsplttr._get_type(str_token))

        int_token = b'2345'
        self.assertEqual(clsplttr._int, clsplttr._get_type(int_token))

        int_token = b'02345'
        self.assertEqual(clsplttr._int, clsplttr._get_type(int_token))

        float_token = b'0.123'
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

    def test__is_sparse(self):
        cs = ColSplitter()
        cs._threshold = 0.8

        charr = np.chararray((10, 3), 5)
        vals1 = [cs._null, 'one', cs._null, 'two', cs._null, cs._null,
                 'three', cs._null, cs._null, cs._null]
        vals2 = [cs._null, 'one', cs._null, cs._null, cs._null, cs._null,
                 'two', cs._null, cs._null, cs._null]
        vals3 = ['NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'one',
                 'NULL', 'NULL', 'NULL']

        for i in range(10):
            charr[i, 0] = vals1[i]
            charr[i, 1] = vals2[i]
            charr[i, 2] = vals3[i]

        self.assertFalse(cs._is_sparse(charr[:, 0]))
        self.assertTrue(cs._is_sparse(charr[:, 1]))
        self.assertTrue(cs._is_sparse(charr[:, 2]))

    def test__try_intify_mv_left(self):
        cs = ColSplitter()
        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = '23.0'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = '0.23'
        charr[1, 2] = cs._null

        res = cs._try_intify_mv_left(charr, 0, 1)
        self.assertEqual(b'23', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[0, 2])

        res = cs._try_intify_mv_left(charr, 1, 1)
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(b'0.23', res[1, 1])
        self.assertEqual(cs._null, res[1, 2])

    def test__try_intify_mv_right(self):
        cs = ColSplitter()
        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = '23.0'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = '0.23'
        charr[1, 2] = cs._null

        res = cs._try_intify_mv_right(charr, 0, 1)
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'23', res[0, 2])

        res = cs._try_intify_mv_right(charr, 1, 1)
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(b'0.23', res[1, 1])
        self.assertEqual(cs._null, res[1, 2])

    def test__try_intify_mv_right_mv_left(self):
        cs = ColSplitter()
        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = '23.0'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = '0.23'
        charr[1, 2] = cs._null

        res = cs._try_intify_mv_right__mv_left(charr, 0, 1)
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'23', res[0, 2])

        res = cs._try_intify_mv_right__mv_left(charr, 1, 1)
        self.assertEqual(b'0.23', res[1, 0])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(cs._null, res[1, 2])

    def test__concat(self):
        cs = ColSplitter()

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = 'abc'
        charr[0, 1] = 'd'
        charr[0, 2] = 'efg'

        charr[1, 0] = 'hijkl'
        charr[1, 1] = 'mnop'
        charr[1, 2] = cs._null

        res = cs._concat(charr, 0, 0, 1, False)
        self.assertEqual(b'abc d', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'efg', res[0, 2])
        self.assertEqual(5, res.itemsize)

        res = cs._concat(charr, 1, 0, 1, True)
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(b'hijkl mnop', res[1, 1])
        self.assertEqual(cs._null, res[1, 2])
        self.assertEqual(10, res.itemsize)

    def test__try_intify_mv_left__concat_right(self):
        cs = ColSplitter()

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = '23.0'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = '0.23'
        charr[1, 2] = 'abc'

        res = cs._try_intify_mv_left__concat_right(charr, 0, 1)
        self.assertEqual(b'23', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[0, 2])

        res = cs._try_intify_mv_left__concat_right(charr, 1, 1)
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(b'0.23 abc', res[1, 2])

    def test__try_intify_mv_right__concat_left(self):
        cs = ColSplitter()

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = '23.0'
        charr[0, 2] = cs._null

        charr[1, 0] = 'abc'
        charr[1, 1] = '0.23'
        charr[1, 2] = cs._null

        res = cs._try_intify_mv_right__concat_left(charr, 0, 1)
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'23', res[0, 2])

        res = cs._try_intify_mv_right__concat_left(charr, 1, 1)
        self.assertEqual(b'abc 0.23', res[1, 0])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(cs._null, res[1, 2])

    def test__try_intify_mv_right__try_fl_mv_left(self):
        cs = ColSplitter()
        cs._token_col_lengths = [3, -1, -1]

        charr = np.chararray((3, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = '23.0'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = '0.2'
        charr[1, 2] = cs._null

        charr[2, 0] = cs._null
        charr[2, 1] = '0.23'
        charr[2, 2] = cs._null

        res = cs._try_intify_mv_right__try_fl_mv_left(charr, 0, 1)
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'23', res[0, 2])

        res = cs._try_intify_mv_right__try_fl_mv_left(charr, 1, 1)
        self.assertEqual(b'0.2', res[1, 0])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(cs._null, res[1, 2])

        res = cs._try_intify_mv_right__try_fl_mv_left(charr, 2, 1)
        self.assertEqual(cs._null, res[2, 0])
        self.assertEqual(b'0.23', res[2, 1])
        self.assertEqual(cs._null, res[2, 2])

    def test__try_fl_mv_left(self):
        cs = ColSplitter()
        cs._token_col_lengths = [2, -1, -1]

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = 'ab'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = 'cde'
        charr[1, 2] = cs._null

        res = cs._try_fl_mv_left(charr, 0, 1)
        self.assertEqual(b'ab', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[0, 2])

        res = cs._try_fl_mv_left(charr, 1, 1)
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(b'cde', res[1, 1])
        self.assertEqual(cs._null, res[1, 2])

    def test__try_fl_mv_right(self):
        cs = ColSplitter()
        cs._token_col_lengths = [-1, -1, 2]

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = 'ab'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = 'cde'
        charr[1, 2] = cs._null

        res = cs._try_fl_mv_right(charr, 0, 1)
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'ab', res[0, 2])

        res = cs._try_fl_mv_right(charr, 1, 1)
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(b'cde', res[1, 1])
        self.assertEqual(cs._null, res[1, 2])

    def test__try_fl_mv(self):
        cs1 = ColSplitter()
        cs1._token_col_lengths = [2, -1, 2]

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs1._null
        charr[0, 1] = 'ab'
        charr[0, 2] = cs1._null

        charr[1, 0] = cs1._null
        charr[1, 1] = 'cde'
        charr[1, 2] = cs1._null

        res = cs1._try_fl_mv(charr, 0, 1)
        self.assertEqual(b'ab', res[0, 0])
        self.assertEqual(cs1._null, res[0, 1])
        self.assertEqual(cs1._null, res[0, 2])

        res = cs1._try_fl_mv(charr, 1, 1)
        self.assertEqual(cs1._null, res[1, 0])
        self.assertEqual(b'cde', res[1, 1])
        self.assertEqual(cs1._null, res[1, 2])

        cs2 = ColSplitter()
        cs2._token_col_lengths = [3, -1, 2]

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs2._null
        charr[0, 1] = 'ab'
        charr[0, 2] = cs2._null

        charr[1, 0] = cs2._null
        charr[1, 1] = 'cde'
        charr[1, 2] = cs2._null

        res = cs2._try_fl_mv(charr, 0, 1)
        self.assertEqual(cs2._null, res[0, 0])
        self.assertEqual(cs2._null, res[0, 1])
        self.assertEqual(b'ab', res[0, 2])

        res = cs2._try_fl_mv(charr, 1, 1)
        self.assertEqual(b'cde', res[1, 0])
        self.assertEqual(cs2._null, res[1, 1])
        self.assertEqual(cs2._null, res[1, 2])

    def test__try_fl_mv_right__try_intify_mv_left(self):
        cs = ColSplitter()
        cs._token_col_lengths = [-1, -1, 3]

        charr = np.chararray((3, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = '1.0'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = '12.0'
        charr[1, 2] = cs._null

        charr[2, 0] = cs._null
        charr[2, 1] = '0.34'
        charr[2, 2] = cs._null

        res = cs._try_fl_mv_right__try_intify_mv_left(charr, 0, 1)
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'1.0', res[0, 2])

        res = cs._try_fl_mv_right__try_intify_mv_left(charr, 1, 1)
        self.assertEqual(b'12', res[1, 0])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(cs._null, res[1, 2])

        res = cs._try_fl_mv_right__try_intify_mv_left(charr, 2, 1)
        self.assertEqual(cs._null, res[2, 0])
        self.assertEqual(b'0.34', res[2, 1])
        self.assertEqual(cs._null, res[2, 2])

    def test__try_fl_mv_left__floatify_mv_right(self):
        cs = ColSplitter()
        cs._token_col_lengths = [2, -1, -1]

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = '23'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = '5'
        charr[1, 2] = cs._null

        res = cs._try_fl_mv_left__floatify_mv_right(charr, 0, 1)
        self.assertEqual(b'23', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[0, 2])

        res = cs._try_fl_mv_left__floatify_mv_right(charr, 1, 1)
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(b'5.0', res[1, 2])

    def test__try_fl_mv_left__mv_right(self):
        cs = ColSplitter()
        cs._token_col_lengths = [2, -1, -1]

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = 'ab'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = 'cde'
        charr[1, 2] = cs._null

        res = cs._try_fl_mv_left__mv_right(charr, 0, 1)
        self.assertEqual(b'ab', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[0, 2])

        res = cs._try_fl_mv_left__mv_right(charr, 1, 1)
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(b'cde', res[1, 2])

    def test__try_fl_mv_right__mv_left(self):
        cs = ColSplitter()
        cs._token_col_lengths = [-1, -1, 2]

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = 'ab'
        charr[0, 2] = cs._null

        charr[1, 0] = cs._null
        charr[1, 1] = 'cde'
        charr[1, 2] = cs._null

        res = cs._try_fl_mv_right__mv_left(charr, 0, 1)
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'ab', res[0, 2])

        res = cs._try_fl_mv_right__mv_left(charr, 1, 1)
        self.assertEqual(b'cde', res[1, 0])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(cs._null, res[1, 2])

    def test__try_fl_mv_left_concat_right(self):
        cs = ColSplitter()
        cs._token_col_lengths = [2, -1, -1]

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = 'ab'
        charr[0, 2] = 'cdef'

        charr[1, 0] = cs._null
        charr[1, 1] = 'ghi'
        charr[1, 2] = 'jklm'

        res = cs._try_fl_mv_left_concat_right(charr, 0, 1)
        self.assertEqual(b'ab', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'cdef', res[0, 2])

        res = cs._try_fl_mv_left_concat_right(charr, 1, 1)
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(b'ghi jklm', res[1, 2])

    def test__try_fl_mv_right_concat_left(self):
        cs = ColSplitter()
        cs._token_col_lengths = [-1, -1, 2]

        charr = np.chararray((2, 3), 5)
        charr[0, 0] = 'cdef'
        charr[0, 1] = 'ab'
        charr[0, 2] = cs._null

        charr[1, 0] = 'ghij'
        charr[1, 1] = 'klm'
        charr[1, 2] = cs._null

        res = cs._try_fl_mv_right_concat_left(charr, 0, 1)
        self.assertEqual(b'cdef', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'ab', res[0, 2])

        res = cs._try_fl_mv_right_concat_left(charr, 1, 1)
        self.assertEqual(b'ghij klm', res[1, 0])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(cs._null, res[1, 2])

    def test__concat_left(self):
        cs = ColSplitter()

        charr = np.chararray((1, 3), 5)
        charr[0, 0] = 'abc'
        charr[0, 1] = 'def'
        charr[0, 2] = 'ghi'

        res = cs._concat_left(charr, 0, 1)
        self.assertEqual(b'abc def', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'ghi', res[0, 2])

    def test__concat_right(self):
        cs = ColSplitter()

        charr = np.chararray((1, 3), 5)
        charr[0, 0] = 'abc'
        charr[0, 1] = 'def'
        charr[0, 2] = 'ghi'

        res = cs._concat_right(charr, 0, 1)
        self.assertEqual(b'abc', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'def ghi', res[0, 2])

    def test__floatify_move_left(self):
        cs = ColSplitter()

        charr = np.chararray((1, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = '23'
        charr[0, 2] = cs._null

        res = cs._floatify_move_left(charr, 0, 1)
        self.assertEqual(b'23.0', res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[0, 2])

    def test__floatify_move_right(self):
        cs = ColSplitter()

        charr = np.chararray((1, 3), 5)
        charr[0, 0] = cs._null
        charr[0, 1] = '23'
        charr[0, 2] = cs._null

        res = cs._floatify_move_right(charr, 0, 1)
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'23.0', res[0, 2])

    def test__merge_cols(self):
        cs = ColSplitter()
        cs._token_col_types = [cs._int, cs._float]
        cs._token_col_lengths = [-1, -1]

        charr = np.chararray((7, 2), 5)
        charr[0, 0] = cs._null
        charr[1, 0] = '23'
        charr[2, 0] = cs._null
        charr[3, 0] = cs._null
        charr[4, 0] = '42'
        charr[5, 0] = '123'
        charr[6, 0] = cs._null

        charr[0, 1] = '12.0'
        charr[1, 1] = cs._null
        charr[2, 1] = '13.0'
        charr[3, 1] = cs._null
        charr[4, 1] = cs._null
        charr[5, 1] = cs._null
        charr[6, 1] = cs._null

        res = cs._merge_cols(charr)
        # self.assertEqual((5, 1), res.shape)
        self.assertEqual(b'12', res[0, 0])
        self.assertEqual(b'23', res[1, 0])
        self.assertEqual(b'13', res[2, 0])
        self.assertEqual(cs._null, res[3, 0])
        self.assertEqual(b'42', res[4, 0])

    def test__has_idx_clash(self):
        cs = ColSplitter()
        charr = np.chararray((5, 3), 5)

        charr[0, 0] = cs._null
        charr[1, 0] = 'a'
        charr[2, 0] = cs._null
        charr[3, 0] = 'b'
        charr[4, 0] = cs._null

        charr[0, 1] = 'c'
        charr[1, 1] = cs._null
        charr[2, 1] = 'd'
        charr[3, 1] = cs._null
        charr[4, 1] = cs._null

        charr[0, 2] = 'e'
        charr[1, 2] = cs._null
        charr[2, 2] = 'f'
        charr[3, 2] = 'g'
        charr[4, 2] = cs._null

        self.assertFalse(cs._has_index_clash(charr, 0, 1))
        self.assertTrue(cs._has_index_clash(charr, 0, 2))

    def test__try_combine_1(self):
        cs = ColSplitter()
        cs._token_col_lengths = [2, -5, -6, 2, -1]
        cs._token_col_types = [cs._str, cs._float, cs._int, cs._str, cs._int]

        charr = np.chararray((5, 5), 5)

        # column 0: should be combined with col 3
        charr[0, 0] = cs._null
        charr[1, 0] = 'ab'
        charr[2, 0] = cs._null
        charr[3, 0] = 'cd'
        charr[4, 0] = cs._null

        # column 1: no combination
        charr[0, 1] = cs._null
        charr[1, 1] = '12.3'
        charr[2, 1] = '45.6'
        charr[3, 1] = cs._null
        charr[4, 1] = cs._null

        # column 2: no combination
        charr[0, 2] = '11'
        charr[1, 2] = cs._null
        charr[2, 2] = '13'
        charr[3, 2] = '14'
        charr[4, 2] = cs._null

        # column 3: combines with col 0
        charr[0, 3] = 'mn'
        charr[1, 3] = cs._null
        charr[2, 3] = 'op'
        charr[3, 3] = cs._null
        charr[4, 3] = 'qr'

        # column 4: no combination
        charr[0, 4] = cs._null
        charr[1, 4] = '12'
        charr[2, 4] = cs._null
        charr[3, 4] = cs._null
        charr[4, 4] = '15'

        res = cs._try_combine(charr, 3, 0)

        self.assertEqual((5, 7), res.shape)
        self.assertEqual([2, -5, -6, 2, -5, -6, -1],
                         cs._token_col_lengths)
        self.assertEqual([cs._str, cs._float, cs._int, cs._str, cs._float,
                          cs._int, cs._int],
                         cs._token_col_types)

        # column 0
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(cs._null, res[2, 0])
        self.assertEqual(cs._null, res[3, 0])
        self.assertEqual(cs._null, res[4, 0])
        # column 1
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(b'45.6', res[2, 1])
        self.assertEqual(cs._null, res[3, 1])
        self.assertEqual(cs._null, res[4, 1])
        # column 2
        self.assertEqual(b'11', res[0, 2])
        self.assertEqual(cs._null, res[1, 2])
        self.assertEqual(b'13', res[2, 2])
        self.assertEqual(cs._null, res[3, 2])
        self.assertEqual(cs._null, res[4, 2])
        # column 3
        self.assertEqual(b'mn', res[0, 3])
        self.assertEqual(b'ab', res[1, 3])
        self.assertEqual(b'op', res[2, 3])
        self.assertEqual(b'cd', res[3, 3])
        self.assertEqual(b'qr', res[4, 3])
        # column 4
        self.assertEqual(cs._null, res[0, 4])
        self.assertEqual(b'12.3', res[1, 4])
        self.assertEqual(cs._null, res[2, 4])
        self.assertEqual(cs._null, res[3, 4])
        self.assertEqual(cs._null, res[4, 4])
        # column 5
        self.assertEqual(cs._null, res[0, 5])
        self.assertEqual(cs._null, res[1, 5])
        self.assertEqual(cs._null, res[2, 5])
        self.assertEqual(b'14', res[3, 5])
        self.assertEqual(cs._null, res[4, 5])
        # column 6
        self.assertEqual(cs._null, res[0, 6])
        self.assertEqual(b'12', res[1, 6])
        self.assertEqual(cs._null, res[2, 6])
        self.assertEqual(cs._null, res[3, 6])
        self.assertEqual(b'15', res[4, 6])

    def test__try_combine_2(self):
        cs = ColSplitter()
        cs._token_col_lengths = [2, -5, -6, 2, -1]
        cs._token_col_types = [cs._str, cs._float, cs._int, cs._str, cs._int]

        charr = np.chararray((5, 5), 5)

        # column 0: no combination
        charr[0, 0] = cs._null
        charr[1, 0] = 'ab'
        charr[2, 0] = cs._null
        charr[3, 0] = 'cd'
        charr[4, 0] = cs._null

        # column 1: no combination
        charr[0, 1] = cs._null
        charr[1, 1] = '12.3'
        charr[2, 1] = '45.6'
        charr[3, 1] = cs._null
        charr[4, 1] = cs._null

        # column 2: should be combined with col 4
        charr[0, 2] = '11'
        charr[1, 2] = cs._null
        charr[2, 2] = '13'
        charr[3, 2] = '14'
        charr[4, 2] = cs._null

        # column 3: no combination
        charr[0, 3] = 'mn'
        charr[1, 3] = cs._null
        charr[2, 3] = 'op'
        charr[3, 3] = cs._null
        charr[4, 3] = 'qr'

        # column 4: combines with col 2
        charr[0, 4] = cs._null
        charr[1, 4] = '12'
        charr[2, 4] = cs._null
        charr[3, 4] = cs._null
        charr[4, 4] = '15'

        res = cs._try_combine(charr, 4, 2)
        self.assertEqual((5, 6), res.shape)
        self.assertEqual([2, -5, -6, 2, -1, 2],
                         cs._token_col_lengths)
        self.assertEqual([cs._str, cs._float, cs._int, cs._str, cs._int,
                          cs._str],
                         cs._token_col_types)
        # column 0
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(b'ab', res[1, 0])
        self.assertEqual(cs._null, res[2, 0])
        self.assertEqual(b'cd', res[3, 0])
        self.assertEqual(cs._null, res[4, 0])
        # column 1
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'12.3', res[1, 1])
        self.assertEqual(b'45.6', res[2, 1])
        self.assertEqual(cs._null, res[3, 1])
        self.assertEqual(cs._null, res[4, 1])
        # column 2
        self.assertEqual(cs._null, res[0, 2])
        self.assertEqual(cs._null, res[1, 2])
        self.assertEqual(cs._null, res[2, 2])
        self.assertEqual(cs._null, res[3, 2])
        self.assertEqual(cs._null, res[4, 2])
        # column 3
        self.assertEqual(cs._null, res[0, 3])
        self.assertEqual(cs._null, res[1, 3])
        self.assertEqual(cs._null, res[2, 3])
        self.assertEqual(cs._null, res[3, 3])
        self.assertEqual(b'qr', res[4, 3])
        # column 4
        self.assertEqual(b'11', res[0, 4])
        self.assertEqual(b'12', res[1, 4])
        self.assertEqual(b'13', res[2, 4])
        self.assertEqual(b'14', res[3, 4])
        self.assertEqual(b'15', res[4, 4])
        # column 5
        self.assertEqual(b'mn', res[0, 5])
        self.assertEqual(cs._null, res[1, 5])
        self.assertEqual(b'op', res[2, 5])
        self.assertEqual(cs._null, res[3, 5])
        self.assertEqual(cs._null, res[4, 5])

    def test__merge_vstr_cols(self):
        cs = ColSplitter()
        cs._token_col_lengths = [-1, -1, 2, 2]
        cs._token_col_types = [cs._str, cs._str, cs._str, cs._str]

        charr = np.chararray((5, 4), 5)

        charr[0, 0] = 'abc'
        charr[1, 0] = cs._null
        charr[2, 0] = 'jkl'
        charr[3, 0] = 'mn'
        charr[4, 0] = cs._null

        charr[0, 1] = 'def'
        charr[1, 1] = 'ghi'
        charr[2, 1] = cs._null
        charr[3, 1] = 'op'
        charr[4, 1] = cs._null

        charr[0, 2] = 'qr'
        charr[1, 2] = 'uv'
        charr[2, 2] = cs._null
        charr[3, 2] = 'yz'
        charr[4, 2] = cs._null

        charr[0, 3] = 'st'
        charr[1, 3] = cs._null
        charr[2, 3] = 'wx'
        charr[3, 3] = cs._null
        charr[4, 3] = cs._null

        res = cs._merge_vstr_cols(charr)

        self.assertEqual((5, 3), res.shape)

        self.assertEqual(b'abc def', res[0, 0])
        self.assertEqual(b'ghi', res[1, 0])
        self.assertEqual(b'jkl', res[2, 0])
        self.assertEqual(b'mn op', res[3, 0])
        self.assertEqual(cs._null, res[4, 0])

        self.assertEqual(b'qr', res[0, 1])
        self.assertEqual(b'uv', res[1, 1])
        self.assertEqual(cs._null, res[2, 1])
        self.assertEqual(b'yz', res[3, 1])
        self.assertEqual(cs._null, res[4, 1])

        self.assertEqual(b'st', res[0, 2])
        self.assertEqual(cs._null, res[1, 2])
        self.assertEqual(b'wx', res[2, 2])
        self.assertEqual(cs._null, res[3, 2])
        self.assertEqual(cs._null, res[4, 2])

    def test__try_combine_cols(self):
        cs = ColSplitter()
        cs._token_col_lengths = [2, -5, -6, 2, -1]
        cs._token_col_types = [cs._str, cs._float, cs._int, cs._str, cs._int]

        charr = np.chararray((5, 5), 5)

        # column 0: should be combined with col 3
        charr[0, 0] = cs._null
        charr[1, 0] = 'ab'
        charr[2, 0] = cs._null
        charr[3, 0] = 'cd'
        charr[4, 0] = cs._null

        # column 1: no combination
        charr[0, 1] = cs._null
        charr[1, 1] = '12.3'
        charr[2, 1] = '45.6'
        charr[3, 1] = cs._null
        charr[4, 1] = cs._null

        # column 2: no combination
        charr[0, 2] = '11'
        charr[1, 2] = cs._null
        charr[2, 2] = '13'
        charr[3, 2] = '14'
        charr[4, 2] = cs._null

        # column 3: combines with col 0
        charr[0, 3] = 'mn'
        charr[1, 3] = cs._null
        charr[2, 3] = 'op'
        charr[3, 3] = cs._null
        charr[4, 3] = 'qr'

        # column 4: no combination
        charr[0, 4] = cs._null
        charr[1, 4] = '12'
        charr[2, 4] = cs._null
        charr[3, 4] = cs._null
        charr[4, 4] = '15'

        res = cs._try_combine_cols(charr)

        self.assertEqual((5, 8), res.shape)
        self.assertEqual([2, -5, -6, 2, -5, -6, -1, 2],
                         cs._token_col_lengths)
        self.assertEqual([cs._str, cs._float, cs._int, cs._str, cs._float,
                          cs._int, cs._int, cs._str],
                         cs._token_col_types)

        # column 0
        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(cs._null, res[2, 0])
        self.assertEqual(cs._null, res[3, 0])
        self.assertEqual(cs._null, res[4, 0])
        # column 1
        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(b'45.6', res[2, 1])
        self.assertEqual(cs._null, res[3, 1])
        self.assertEqual(cs._null, res[4, 1])
        # column 2
        self.assertEqual(cs._null, res[0, 2])
        self.assertEqual(cs._null, res[1, 2])
        self.assertEqual(cs._null, res[2, 2])
        self.assertEqual(cs._null, res[3, 2])
        self.assertEqual(cs._null, res[4, 2])
        # column 3
        self.assertEqual(cs._null, res[0, 3])
        self.assertEqual(b'ab', res[1, 3])
        self.assertEqual(cs._null, res[2, 3])
        self.assertEqual(b'cd', res[3, 3])
        self.assertEqual(b'qr', res[4, 3])
        # column 4
        self.assertEqual(cs._null, res[0, 4])
        self.assertEqual(b'12.3', res[1, 4])
        self.assertEqual(cs._null, res[2, 4])
        self.assertEqual(cs._null, res[3, 4])
        self.assertEqual(cs._null, res[4, 4])
        # column 5
        self.assertEqual(cs._null, res[0, 5])
        self.assertEqual(cs._null, res[1, 5])
        self.assertEqual(cs._null, res[2, 5])
        self.assertEqual(cs._null, res[3, 5])
        self.assertEqual(cs._null, res[4, 5])
        # column 6
        self.assertEqual(b'11', res[0, 6])
        self.assertEqual(b'12', res[1, 6])
        self.assertEqual(b'13', res[2, 6])
        self.assertEqual(b'14', res[3, 6])
        self.assertEqual(b'15', res[4, 6])
        # column 7
        self.assertEqual(b'mn', res[0, 7])
        self.assertEqual(cs._null, res[1, 7])
        self.assertEqual(b'op', res[2, 7])
        self.assertEqual(cs._null, res[3, 7])
        self.assertEqual(cs._null, res[4, 7])

    def test__merge_col_to_left(self):
        cs = ColSplitter()

        charr = np.chararray((3, 2), 5)

        charr[0, 0] = cs._null
        charr[1, 0] = cs._null
        charr[2, 0] = 'abc'

        charr[0, 1] = cs._null
        charr[1, 1] = 'def'
        charr[2, 1] = 'ghi'

        res = cs._merge_col_to_left(charr, 1)

        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(b'def', res[1, 0])
        self.assertEqual(b'abc ghi', res[2, 0])

        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(cs._null, res[2, 1])

    def test__push_to_right(self):
        cs = ColSplitter()

        charr = np.chararray((3, 4), 5)
        charr.fill(cs._null)

        charr[1, 0] = 'a'
        charr[1, 1] = 'b'
        charr[1, 2] = 'c'

        res = cs._push_to_right(charr, 1, 0)

        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(cs._null, res[2, 0])

        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'a', res[1, 1])
        self.assertEqual(cs._null, res[2, 1])

        self.assertEqual(cs._null, res[0, 2])
        self.assertEqual(b'b', res[1, 2])
        self.assertEqual(cs._null, res[2, 2])

        self.assertEqual(cs._null, res[0, 3])
        self.assertEqual(b'c', res[1, 3])
        self.assertEqual(cs._null, res[2, 3])

        res = cs._push_to_right(charr, 1, 1)

        self.assertEqual((3, 5), res.shape)

        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(cs._null, res[2, 0])

        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(cs._null, res[2, 1])

        self.assertEqual(cs._null, res[0, 2])
        self.assertEqual(b'a', res[1, 2])
        self.assertEqual(cs._null, res[2, 2])

        self.assertEqual(cs._null, res[0, 3])
        self.assertEqual(b'b', res[1, 3])
        self.assertEqual(cs._null, res[2, 3])

        self.assertEqual(cs._null, res[0, 4])
        self.assertEqual(b'c', res[1, 4])
        self.assertEqual(cs._null, res[2, 4])

    def test__mv_from_vstr_col(self):
        cs = ColSplitter()
        cs._considered_lengths = [2, 3]
        cs._token_col_lengths = [-1, -1]

        charr = np.chararray((3, 2), 5)

        charr[0, 0] = cs._null
        charr[1, 0] = cs._null
        charr[2, 0] = cs._null

        charr[0, 1] = cs._null
        charr[1, 1] = b'abcde'
        charr[2, 1] = b'fg'

        res = cs._mv_from_vstr_col(charr, 1, cs._str)

        self.assertEqual((3, 3), res.shape)

        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(cs._null, res[2, 0])

        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'abcde', res[1, 1])
        self.assertEqual(cs._null, res[2, 1])

        self.assertEqual(cs._null, res[0, 2])
        self.assertEqual(cs._null, res[1, 2])
        self.assertEqual(b'fg', res[2, 2])

        cs._token_col_lengths = [2, -1]

        charr = np.chararray((4, 2), 5)

        charr[0, 0] = cs._null
        charr[1, 0] = cs._null
        charr[2, 0] = cs._null
        charr[3, 0] = cs._null

        charr[0, 1] = cs._null
        charr[1, 1] = b'abcde'
        charr[2, 1] = b'fg'
        charr[3, 1] = b'hij'

        res = cs._mv_from_vstr_col(charr, 1, cs._str)

        self.assertEqual((4, 3), res.shape)

        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(b'fg', res[2, 0])
        self.assertEqual(cs._null, res[3, 0])

        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'abcde', res[1, 1])
        self.assertEqual(cs._null, res[2, 1])
        self.assertEqual(cs._null, res[3, 1])

        self.assertEqual(cs._null, res[0, 2])
        self.assertEqual(cs._null, res[1, 2])
        self.assertEqual(cs._null, res[2, 2])
        self.assertEqual(b'hij', res[3, 2])

    def test__get_col_fixed_len(self):
        cs = ColSplitter()
        cs._considered_lengths = [2, 3]

        charr = np.chararray((5, 2), 5)

        charr[0, 0] = 'ab'
        charr[1, 0] = 'cde'
        charr[2, 0] = 'fgh'
        charr[3, 0] = 'ijhkl'
        charr[4, 0] = 'mn'

        charr[0, 1] = 'ab'
        charr[1, 1] = 'cde'
        charr[2, 1] = 'fgh'
        charr[3, 1] = 'ijhkl'
        charr[4, 1] = 'mno'

        res = cs._get_col_fixed_len(charr[:, 0])
        self.assertEqual(2, res)

        res = cs._get_col_fixed_len(charr[:, 1])
        self.assertEqual(3, res)

    def test__mv_from_fstr_col(self):
        cs = ColSplitter()
        cs._considered_lengths = [2, 3]
        cs._token_col_lengths = [-1, 3]
        cs._considered_lengths = [2, 3, 4]

        charr = np.chararray((4, 2), 5)

        charr[0, 0] = cs._null
        charr[1, 0] = cs._null
        charr[2, 0] = cs._null
        charr[3, 0] = cs._null

        charr[0, 1] = cs._null
        charr[1, 1] = 'abcde'
        charr[2, 1] = 'fg'
        charr[3, 1] = 'hij'

        res = cs._mv_from_fstr_col(charr, 1, 3)

        self.assertEqual((4, 3), res.shape)

        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(cs._null, res[2, 0])
        self.assertEqual(cs._null, res[3, 0])

        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(cs._null, res[2, 1])
        self.assertEqual(b'hij', res[3, 1])

        self.assertEqual(cs._null, res[0, 2])
        self.assertEqual(b'abcde', res[1, 2])
        self.assertEqual(b'fg', res[2, 2])
        self.assertEqual(cs._null, res[2, 0])

        cs._token_col_lengths = [2, 3]

        charr = np.chararray((4, 2), 5)

        charr[0, 0] = cs._null
        charr[1, 0] = cs._null
        charr[2, 0] = cs._null
        charr[3, 0] = cs._null

        charr[0, 1] = cs._null
        charr[1, 1] = 'abcde'
        charr[2, 1] = 'fg'
        charr[3, 1] = 'hij'

        res = cs._mv_from_fstr_col(charr, 1, 3)

        self.assertEqual((4, 3), res.shape)

        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(b'fg', res[2, 0])
        self.assertEqual(cs._null, res[3, 0])

        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(cs._null, res[1, 1])
        self.assertEqual(cs._null, res[2, 1])
        self.assertEqual(b'hij', res[3, 1])

        self.assertEqual(cs._null, res[0, 2])
        self.assertEqual(b'abcde', res[1, 2])
        self.assertEqual(cs._null, res[2, 2])
        self.assertEqual(cs._null, res[2, 2])

    def test__mv_from_non_str_col(self):
        cs = ColSplitter()
        cs._considered_lengths = [2, 3]
        cs._token_col_lengths = [3]

        charr = np.chararray((5, 2), 5)

        charr[0, 0] = cs._null
        charr[1, 0] = cs._null
        charr[2, 0] = 'abc'
        charr[3, 0] = cs._null
        charr[4, 0] = cs._null

        charr[0, 1] = cs._null
        charr[1, 1] = '42'
        charr[2, 1] = 'fgh'
        charr[3, 1] = 'fg'
        charr[4, 1] = 'ijk'

        res = cs._mv_from_non_str_col(charr, 1, cs._int, cs._str)

        self.assertEqual((5, 3), res.shape)

        self.assertEqual(cs._null, res[0, 0])
        self.assertEqual(cs._null, res[1, 0])
        self.assertEqual(b'abc', res[2, 0])
        self.assertEqual(cs._null, res[3, 0])
        self.assertEqual(b'ijk', res[4, 0])

        self.assertEqual(cs._null, res[0, 1])
        self.assertEqual(b'42', res[1, 1])
        self.assertEqual(cs._null, res[2, 1])
        self.assertEqual(cs._null, res[3, 1])
        self.assertEqual(cs._null, res[4, 1])

        self.assertEqual(cs._null, res[0, 2])
        self.assertEqual(cs._null, res[1, 2])
        self.assertEqual(b'fgh', res[2, 2])
        self.assertEqual(b'fg', res[3, 2])
        self.assertEqual(cs._null, res[4, 2])