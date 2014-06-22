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
            charr[i,0] = vals1[i]
            charr[i,1] = vals2[i]
            charr[i,2] = vals3[i]
        
        self.assertFalse(cs._is_sparse(charr[:,0]))
        self.assertTrue(cs._is_sparse(charr[:,1]))
        self.assertTrue(cs._is_sparse(charr[:,2]))

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