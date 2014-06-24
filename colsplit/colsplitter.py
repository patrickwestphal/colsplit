import numpy as np


class ColSplitter(object):
    """TODO: implement
    TODO: test
    """

    _int = 'int'
    _float = 'float'
    _str = 'str'
    _invalid = 'invalid'
    _fixed_len = 'fixed len'
    _null = b'NULL'
    _null_type = 'null'
    _valid = 'valid'
    _mixed = 'mixed'

    ###########################################################################
    # <merge action methods>
    #
    # - move (mv)
    # - try to cast a float to an int (intify) and move
    # - try to move a value of arbitrary type to a fixed length string cell
    #   (fl mv)
    # - concatenate with value of neighbor cell (concat)
    # - 'cast' an integer value to float, i.e. append '.0' (floatify) and move
    #

    def dummy(self, arr, line_idx, col_idx):
        raise NotImplementedError("Just a dummy -- to be replaced")

    def _mv_left(self, arr, line_idx, col_idx):
        """Moves the cell content of the considered cell to its left neighbor
        """
        arr[line_idx, col_idx-1] = arr[line_idx, col_idx]
        arr[line_idx, col_idx] = self._null

        return arr

    def _mv_right(self, arr, line_idx, col_idx):
        """Moves the cell content of the considered cell to its right neighbor
        """
        arr[line_idx, col_idx+1] = arr[line_idx, col_idx]
        arr[line_idx, col_idx] = self._null

        return arr

    def _try_intify_mv_left(self, arr, line_idx, col_idx):
        """This method tries to 'cast' a float value to an integer and move it
        to the left neighbor cell
        """
        curr_val = arr[line_idx, col_idx]
        # since the actual input string was detected to be a float, there can
        # only be one dot
        nonfrac, frac = curr_val.decode('utf8').split('.')
        if frac == '0':
            arr[line_idx, col_idx-1] = nonfrac
            arr[line_idx, col_idx] = self._null

        return arr

    def _try_intify_mv_right(self, arr, line_idx, col_idx):
        """This method tries to 'cast' a float value to an integer and move it
        to the right neighbor cell
        """
        curr_val = arr[line_idx, col_idx]
        nonfrac, frac = curr_val.decode('utf8').split('.')
        if frac == '0':
            arr[line_idx, col_idx+1] = nonfrac
            arr[line_idx, col_idx] = self._null

        return arr

    def _try_intify_mv_right__mv_left(self, arr, line_idx, col_idx):
        """used in case
             vstr (NULL) | float | int (NULL)
        """
        curr_val = arr[line_idx, col_idx]
        nonfrac, frac = curr_val.decode('utf8').split('.')
        if frac == '0':
            arr[line_idx, col_idx+1] = nonfrac
            arr[line_idx, col_idx] = self._null
        else:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null

        return arr

    def _concat(self, arr, line_idx, col_idx_l, col_idx_r, to_right):
        """@param to_right: controls whether the resulting concatenated value
        will be written to the left or right cell
        """
        val1 = arr[line_idx, col_idx_l]
        val2 = arr[line_idx, col_idx_r]
        new_val = val1 + b' ' + val2

        if len(new_val) > arr.itemsize:
            new_itemsize = 2 * arr.itemsize
            new_arr = np.chararray(arr.shape, new_itemsize)
            np.copyto(new_arr, arr)
            arr = new_arr

        if to_right:
            arr[line_idx, col_idx_l] = self._null
            arr[line_idx, col_idx_r] = new_val
        else:
            arr[line_idx, col_idx_l] = new_val
            arr[line_idx, col_idx_r] = self._null

        return arr

    def _try_intify_mv_left__concat_right(self, arr, line_idx, col_idx):
        """This method is used in cases where there is an integer column on the
        left and a (non-fixed) string column on the right. Moreover the
        considered column is a float column, the left neighbor cell is empty
        and the right neighbor cell is not:

             int (NULL) | float | vstr (NOT NULL)

        Thus it is
        1) first tried to 'cast' the float value to an integer and move it to
           the left.
        2) If this does not work, the float value is concated (from the left)
           to the right neighbor cell
        """
        curr_val = arr[line_idx, col_idx]
        # 1)
        nonfrac, frac = curr_val.decode('utf8').split('.')
        if frac == '0':
            arr[line_idx, col_idx-1] = nonfrac
            arr[line_idx, col_idx] = self._null
        else:
            # 2)
            arr = self._concat(arr, line_idx, col_idx, col_idx+1, True)

        return arr

    def _try_intify_mv_right__concat_left(self, arr, line_idx, col_idx):
        """used in case  vstr (NOT NULL) | float | int (NULL)
        """
        curr_val = arr[line_idx, col_idx]
        nonfrac, frac = curr_val.decode('utf8').split('.')

        if frac == '0':
            arr[line_idx, col_idx+1] = nonfrac
            arr[line_idx, col_idx] = self._null
        else:
            arr = self._concat(arr, line_idx, col_idx-1, col_idx, False)

        return arr

    def _try_intify_mv_right__try_fl_mv_left(self, arr, line_idx, col_idx):
        """Tries to
        1) 'cast' a float value to int and move it to the right
           neighbor cell.
        If this does not work, this method also tries to
        2) move the considered value to the fixed string left neighbor cell.
        The method is used in the following case

             fstr (NULL) | float | int (NULL)
        """
        curr_val = arr[line_idx, col_idx]
        # 1)
        nonfrac, frac = curr_val.decode('utf8').split('.')
        if frac == '0':
            arr[line_idx, col_idx+1] = nonfrac
            arr[line_idx, col_idx] = self._null
        else:
            # 2)
            l_col_len = self._token_col_lengths[col_idx-1]

            if len(curr_val) == l_col_len:
                arr[line_idx, col_idx-1] = curr_val
                arr[line_idx, col_idx] = self._null

        return arr

    def _try_fl_mv_left(self, arr, line_idx, col_idx):
        """This method is used in cases where the considered column is of
        arbitrary type with a left neighbor being a string column. Since the
        left neighbor only contains strings with a fixed length, it is checked
        whether the currently considered cell value has a suitable string
        length and could be moved to the empty left neighbor cell
        """
        curr_val = arr[line_idx, col_idx]
        l_col_len = self._token_col_lengths[col_idx-1]

        if len(curr_val) == l_col_len:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null

        return arr

    def _try_fl_mv_right(self, arr, line_idx, col_idx):
        """This method is used in cases where the considered column is of
        arbitrary type with a right neighbor being a string column. Since the
        right neighbor only contains strings with a fixed length, it is checked
        whether the currently considered cell value has a suitable string
        length and could be moved to the empty right neighbor cell
        """
        curr_val = arr[line_idx, col_idx]
        r_col_len = self._token_col_lengths[col_idx+1]

        if len(curr_val) == r_col_len:
            arr[line_idx, col_idx+1] = curr_val
            arr[line_idx, col_idx] = self._null

        return arr

    def _try_fl_mv(self, arr, line_idx, col_idx):
        """This method is used in cases where the considered column is of
        arbitrary type with a left and right neighbor being a string column.
        Since the left and right neighbor only contain strings with a fixed
        length, it is checked whether the currently considered cell value has
        a suitable string length and could be moved to on of the empty left
        neighbor cells
        """
        curr_val = arr[line_idx, col_idx]
        curr_val_len = len(curr_val)
        # try left column first
        l_col_len = self._token_col_lengths[col_idx-1]

        if curr_val_len == l_col_len:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null

        else:
            # try right column
            r_col_len = self._token_col_lengths[col_idx+1]

            if curr_val_len == r_col_len:
                arr[line_idx, col_idx+1] = curr_val
                arr[line_idx, col_idx] = self._null

        return arr

    def _try_fl_mv_right__try_intify_mv_left(self, arr, line_idx, col_idx):
        """This method is used in case there is an integer column on the left
        and a fixed string column on the right. Moreover the considered column
        is a float column and both, the left and right neighbor cells are
        empty:

             int (NULL) | float | fstr (NULL)

        Thus it is
        1) first tried to move the float value to the str column. This only
           works if the str length of the str column mathches the float value
           string length.
        2) If not it is tried to 'cast' the float value to an integer
        """
        curr_val = arr[line_idx, col_idx]

        # 1)
        r_col_len = self._token_col_lengths[col_idx+1]
        if len(curr_val) == r_col_len:
            arr[line_idx, col_idx+1] = curr_val
            arr[line_idx, col_idx] = self._null
        else:
            # 2)
            nonfrac, frac = curr_val.decode('utf8').split('.')
            if frac == '0':
                arr[line_idx, col_idx-1] = nonfrac
                arr[line_idx, col_idx] = self._null

        return arr

    def _try_fl_mv_left__floatify_mv_right(self, arr, line_idx, col_idx):
        """used in case of

             fstr (NULL) | int | float (NULL)
        """
        curr_val = arr[line_idx, col_idx]
        l_col_len = self._token_col_lengths[col_idx-1]

        if len(curr_val) == l_col_len:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null
        else:
            new_r_val = curr_val + b'.0'
            arr[line_idx, col_idx+1] = new_r_val
            arr[line_idx, col_idx] = self._null

        return arr

    def _try_fl_mv_left__mv_right(self, arr, line_idx, col_idx):
        """used in case

             fstr (NULL) | str | vstr (NULL)
        """
        # try to move to left
        curr_val = arr[line_idx, col_idx]
        l_col_len = self._token_col_lengths[col_idx-1]

        if len(curr_val) == l_col_len:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null

        else:
            # move to right neighbor
            arr[line_idx, col_idx+1] = curr_val
            arr[line_idx, col_idx] = self._null

        return arr

    def _try_fl_mv_right__mv_left(self, arr, line_idx, col_idx):
        """used in case

             vstr (NULL) | <type> | fstr (NULL)
        """
        curr_val = arr[line_idx, col_idx]
        r_col_len = self._token_col_lengths[col_idx+1]

        if len(curr_val) == r_col_len:
            arr[line_idx, col_idx+1] = curr_val
            arr[line_idx, col_idx] = self._null

        else:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null

        return arr

    def _try_fl_mv_left_concat_right(self, arr, line_idx, col_idx):
        """used in case

             fstr (NULL) | str | vstr (NOT NULL)
        """
        # try to move to left
        curr_val = arr[line_idx, col_idx]
        l_col_len = self._token_col_lengths[col_idx-1]

        if len(curr_val) == l_col_len:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null

        else:
            # concat to right neighbor
            arr = self._concat(arr, line_idx, col_idx, col_idx+1, True)

        return arr

    def _try_fl_mv_right_concat_left(self, arr, line_idx, col_idx):
        """used in case

             vstr (NOT NULL) | <type> | fstr (NULL)
        """
        curr_val = arr[line_idx, col_idx]
        r_col_len = self._token_col_lengths[col_idx+1]

        if len(curr_val) == r_col_len:
            arr[line_idx, col_idx+1] = curr_val
            arr[line_idx, col_idx] = self._null

        else:
            # concat to left neighbor
            arr = self._concat(arr, line_idx, col_idx-1, col_idx, False)

        return arr

    def _concat_left(self, arr, line_idx, col_idx):
        """used in case the considered column has a left neighbor string column
        with non-fixed string length
        """
        return self._concat(arr, line_idx, col_idx-1, col_idx, False)

    def _concat_right(self, arr, line_idx, col_idx):
        """used in case the considered column has a right neighbor string
        column with non-fixed string length
        """
        return self._concat(arr, line_idx, col_idx, col_idx+1, True)

    def _floatify_move_left(self, arr, line_idx, col_idx):
        """used in case a value from an int column has an empty float cell
        neighbor
        """
        curr_val = arr[line_idx, col_idx]
        new_l_val = curr_val + b'.0'
        arr[line_idx, col_idx-1] = new_l_val
        arr[line_idx, col_idx] = self._null

        return arr

    def _floatify_move_right(self, arr, line_idx, col_idx):
        """Used in case a value from an int column has an empty float cell
        neighbor
        """
        curr_val = arr[line_idx, col_idx]
        new_r_val = curr_val + b'.0'
        arr[line_idx, col_idx+1] = new_r_val
        arr[line_idx, col_idx] = self._null

        return arr

    #
    # </merge action methods>
    ###########################################################################

    def __init__(self, delimiter=' ', threshold=0.7):

        F = False
        T = True
        INT = self._int
        FLT = self._float
        STR = self._str
        NVD = self._invalid
        # 0 --> type of the column to the left
        # 1 --> has the column to the left a fixed string length?
        # 2 --> is the left neighbor cell empty?
        # 3 --> type of the considered column
        # 4 --> has the considered column a fixed string length?
        # 5 --> type of the column to the right
        # 6 --> has the column to the righ a fixed string length?
        # 7 --> is the left neighbor cell empty?
        self._merge_cases = {
            # 0   1  2   3   4   5   6  7
            (INT, F, T, INT, F, INT, F, T): self._mv_left,
            (INT, F, T, INT, F, INT, F, F): self._mv_left,
            (INT, F, T, INT, F, FLT, F, T): self._mv_left,
            (INT, F, T, INT, F, FLT, F, F): self._mv_left,
            (INT, F, T, INT, F, STR, T, T): self._mv_left,
            (INT, F, T, INT, F, STR, T, F): self._mv_left,
            (INT, F, T, INT, F, STR, F, T): self._mv_left,
            (INT, F, T, INT, F, STR, F, F): self._mv_left,
            (INT, F, T, INT, F, NVD, F, F): self._mv_left,
            (INT, F, T, FLT, F, INT, F, T): self._try_intify_mv_left,
            (INT, F, T, FLT, F, INT, F, F): self._try_intify_mv_left,
            (INT, F, T, FLT, F, FLT, F, T): self._mv_right,
            (INT, F, T, FLT, F, FLT, F, F): self._try_intify_mv_left,
            (INT, F, T, FLT, F, STR, T, T): self._try_fl_mv_right__try_intify_mv_left,
            (INT, F, T, FLT, F, STR, T, F): self._try_intify_mv_left,
            (INT, F, T, FLT, F, STR, F, T): self._mv_right,
            (INT, F, T, FLT, F, STR, F, F): self._try_intify_mv_left__concat_right,
            (INT, F, T, FLT, F, NVD, F, F): self._try_intify_mv_left,
            (INT, F, T, STR, T, STR, T, F): self._try_fl_mv_right,
            (INT, F, T, STR, T, STR, F, T): self._concat_right,
            (INT, F, T, STR, T, STR, F, F): self._mv_right,
            (INT, F, T, STR, F, STR, T, T): self._try_fl_mv_right,
            (INT, F, T, STR, F, STR, F, T): self._mv_right,
            (INT, F, T, STR, F, STR, F, F): self._concat_right,
            (INT, F, F, INT, F, INT, F, T): self._mv_right,
            (INT, F, F, INT, F, FLT, F, T): self._floatify_move_right,
            (INT, F, F, INT, F, STR, T, T): self._try_fl_mv_right,
            (INT, F, F, INT, F, STR, F, T): self._mv_right,
            (INT, F, F, INT, F, STR, F, F): self._concat_right,
            (INT, F, F, FLT, F, INT, F, T): self._try_intify_mv_right,
            (INT, F, F, FLT, F, FLT, F, T): self._mv_right,
            (INT, F, F, FLT, F, STR, T, T): self._try_fl_mv_right,
            (INT, F, F, FLT, F, STR, F, T): self._mv_right,
            (INT, F, F, FLT, F, STR, F, F): self._concat_right,
            (INT, F, F, STR, T, STR, T, T): self._try_fl_mv_right,
            (INT, F, F, STR, T, STR, F, T): self._mv_right,
            (INT, F, F, STR, T, STR, F, F): self._concat_right,
            (INT, F, F, STR, F, STR, T, T): self._try_fl_mv_right,
            (INT, F, F, STR, F, STR, F, T): self._mv_right,
            (INT, F, F, STR, F, STR, F, F): self._concat_right,
            (FLT, F, T, INT, F, INT, F, T): self._mv_right,
            (FLT, F, T, INT, F, INT, F, F): self._floatify_move_left,
            (FLT, F, T, INT, F, FLT, F, T): self._floatify_move_left,
            (FLT, F, T, INT, F, FLT, F, F): self._floatify_move_left,
            (FLT, F, T, INT, F, STR, T, T): self._floatify_move_left,
            (FLT, F, T, INT, F, STR, T, F): self._floatify_move_left,
            (FLT, F, T, INT, F, STR, F, T): self._floatify_move_left,  # TODO: discuss
            (FLT, F, T, INT, F, STR, F, F): self._floatify_move_left,
            (FLT, F, T, FLT, F, INT, F, T): self._mv_left,
            (FLT, F, T, FLT, F, INT, F, F): self._mv_left,
            (FLT, F, T, FLT, F, FLT, F, T): self._mv_left,
            (FLT, F, T, FLT, F, FLT, F, F): self._mv_left,
            (FLT, F, T, FLT, F, STR, T, T): self._mv_left,
            (FLT, F, T, FLT, F, STR, T, F): self._mv_left,
            (FLT, F, T, FLT, F, STR, F, T): self._mv_left,
            (FLT, F, T, FLT, F, STR, F, F): self._mv_left,
            (FLT, F, T, STR, T, STR, T, T): self._try_fl_mv_right,
            (FLT, F, T, STR, T, STR, F, T): self._mv_right,
            (FLT, F, T, STR, T, STR, F, F): self._concat_right,
            (FLT, F, T, STR, F, STR, T, T): self._try_fl_mv_right,
            (FLT, F, T, STR, F, STR, F, T): self._mv_right,
            (FLT, F, T, STR, F, STR, F, F): self._concat_right,
            (FLT, F, F, INT, F, INT, F, T): self._mv_right,
            (FLT, F, F, INT, F, FLT, F, T): self._floatify_move_right,
            (FLT, F, F, INT, F, STR, T, T): self._try_fl_mv_right,
            (FLT, F, F, INT, F, STR, F, T): self._mv_right,
            (FLT, F, F, INT, F, STR, F, F): self._concat_right,
            (FLT, F, F, FLT, F, INT, F, T): self._try_intify_mv_right,
            (FLT, F, F, FLT, F, FLT, F, T): self._mv_right,
            (FLT, F, F, FLT, F, STR, T, T): self._try_fl_mv_right,
            (FLT, F, F, FLT, F, STR, F, T): self._mv_right,
            (FLT, F, F, FLT, F, STR, F, F): self._concat_right,
            (FLT, F, F, STR, T, STR, T, T): self._try_fl_mv_right,
            (FLT, F, F, STR, T, STR, F, T): self._mv_right,
            (FLT, F, F, STR, T, STR, F, F): self._concat_right,
            (FLT, F, F, STR, F, STR, T, T): self._try_fl_mv_right,
            (FLT, F, F, STR, F, STR, F, T): self._mv_right,
            (FLT, F, F, STR, F, STR, F, F): self._concat_right,
            (STR, T, T, INT, F, INT, F, T): self._mv_right,
            (STR, T, T, INT, F, INT, F, F): self._try_fl_mv_left,
            (STR, T, T, INT, F, FLT, F, T): self._try_fl_mv_left__floatify_mv_right,
            (STR, T, T, INT, F, FLT, F, T): self._floatify_move_right,
            (STR, T, T, INT, F, FLT, F, F): self._try_fl_mv_left,
            (STR, T, T, INT, F, STR, T, T): self._try_fl_mv,
            (STR, T, T, INT, F, STR, T, F): self._try_fl_mv_left,
            (STR, T, T, INT, F, STR, F, T): self._mv_right,  # TODO: discuss
            (STR, T, T, INT, F, STR, F, F): self._concat_right,  # TODO: discuss
            (STR, T, T, FLT, F, INT, F, T): self._try_intify_mv_right__try_fl_mv_left,  # TODO: discuss
            (STR, T, T, FLT, F, INT, F, F): self._try_fl_mv_left,
            (STR, T, T, FLT, F, FLT, F, T): self._mv_right,
            (STR, T, T, FLT, F, FLT, F, F): self._try_fl_mv_left,
            (STR, T, T, FLT, F, STR, T, T): self._try_fl_mv,
            (STR, T, T, FLT, F, STR, T, F): self._try_fl_mv_left,
            (STR, T, T, FLT, F, STR, F, T): self._concat_right,  # TODO: discuss
            (STR, T, T, FLT, F, STR, F, F): self._try_fl_mv_left,
            (STR, T, T, FLT, F, NVD, F, F): self._try_fl_mv_left,
            (STR, T, T, STR, T, INT, F, T): self._try_fl_mv_left,
            (STR, T, T, STR, T, INT, F, F): self._try_fl_mv_left,
            (STR, T, T, STR, T, FLT, F, T): self._try_fl_mv_left,
            (STR, T, T, STR, T, FLT, F, F): self._try_fl_mv_left,
            (STR, T, T, STR, T, STR, T, T): self._try_fl_mv,
            (STR, T, T, STR, T, STR, T, F): self._try_fl_mv_left,
            (STR, T, T, STR, T, STR, F, T): self._try_fl_mv_left__mv_right,
            (STR, T, T, STR, T, STR, F, F): self._try_fl_mv_left_concat_right,
            (STR, T, T, STR, T, NVD, F, F): self._try_fl_mv_left,
            (STR, T, T, STR, F, INT, F, T): self._try_fl_mv_left,
            (STR, T, T, STR, F, INT, F, F): self._try_fl_mv_left,
            (STR, T, T, STR, F, FLT, F, T): self._try_fl_mv_left,
            (STR, T, T, STR, F, FLT, F, F): self._try_fl_mv_left,
            (STR, T, T, STR, F, STR, T, T): self._try_fl_mv,
            (STR, T, T, STR, F, STR, T, F): self._try_fl_mv_left,
            (STR, T, T, STR, F, STR, F, T): self._try_fl_mv_left__mv_right,
            (STR, T, T, STR, F, STR, F, F): self._try_fl_mv_left_concat_right,
            (STR, T, T, STR, F, NVD, F, F): self._try_fl_mv_left,
            (STR, T, F, INT, F, INT, F, T): self._mv_right,
            (STR, T, F, INT, F, FLT, F, T): self._floatify_move_right,
            (STR, T, F, INT, F, STR, T, T): self._try_fl_mv_right,
            (STR, T, F, INT, F, STR, F, T): self._mv_right,
            (STR, T, F, INT, F, STR, F, F): self._concat_right,
            (STR, T, F, FLT, F, INT, F, T): self._try_intify_mv_right,
            (STR, T, F, FLT, F, FLT, F, T): self._mv_right,
            (STR, T, F, FLT, F, STR, T, T): self._try_fl_mv_right,
            (STR, T, F, FLT, F, STR, F, T): self._mv_right,
            (STR, T, F, FLT, F, STR, F, F): self._concat_right,
            (STR, T, F, STR, T, STR, T, T): self._try_fl_mv_right,
            (STR, T, F, STR, T, STR, F, T): self._mv_right,
            (STR, T, F, STR, T, STR, F, F): self._concat_right,
            (STR, T, F, STR, F, STR, T, T): self._try_fl_mv_right,
            (STR, T, F, STR, F, STR, F, T): self._mv_right,
            (STR, T, F, STR, F, STR, F, F): self._concat_right,
            (STR, F, T, INT, F, INT, F, T): self._mv_right,
            (STR, F, T, INT, F, INT, F, F): self._mv_left,
            (STR, F, T, INT, F, FLT, F, T): self._floatify_move_right,
            (STR, F, T, INT, F, FLT, F, F): self._mv_left,
            (STR, F, T, INT, F, STR, T, T): self._mv_left,  # TODO: discuss
            (STR, F, T, INT, F, STR, T, F): self._mv_left,
            (STR, F, T, INT, F, STR, F, T): self._mv_left,
            (STR, F, T, INT, F, STR, F, F): self._mv_left,
            (STR, F, T, INT, F, NVD, F, F): self._mv_left,
            (STR, F, T, FLT, F, INT, F, T): self._try_intify_mv_right__mv_left,
            (STR, F, T, FLT, F, INT, F, F): self._mv_left,
            (STR, F, T, FLT, F, FLT, F, T): self._mv_right,
            (STR, F, T, FLT, F, FLT, F, F): self._mv_left,
            (STR, F, T, FLT, F, STR, T, T): self._mv_left,  # TODO: discuss
            (STR, F, T, FLT, F, STR, T, F): self._mv_left,
            (STR, F, T, FLT, F, STR, F, T): self._mv_left,
            (STR, F, T, FLT, F, STR, F, F): self._mv_left,
            (STR, F, T, FLT, F, NVD, F, F): self._mv_left,
            (STR, F, T, STR, T, INT, F, T): self._mv_left,
            (STR, F, T, STR, T, INT, F, F): self._mv_left,
            (STR, F, T, STR, T, FLT, F, T): self._mv_left,
            (STR, F, T, STR, T, FLT, F, F): self._mv_left,
            (STR, F, T, STR, T, STR, T, T): self._try_fl_mv_right__mv_left,
            (STR, F, T, STR, T, STR, T, F): self._mv_left,
            (STR, F, T, STR, T, STR, F, T): self._mv_left,
            (STR, F, T, STR, T, STR, F, F): self._mv_left,
            (STR, F, T, STR, T, NVD, F, F): self._mv_left,
            (STR, F, T, STR, F, INT, F, T): self._mv_left,
            (STR, F, T, STR, F, INT, F, F): self._mv_left,
            (STR, F, T, STR, F, FLT, F, T): self._mv_left,
            (STR, F, T, STR, F, FLT, F, F): self._mv_left,
            (STR, F, T, STR, F, STR, T, T): self._try_fl_mv_right__mv_left,
            (STR, F, T, STR, F, STR, T, F): self._mv_left,
            (STR, F, T, STR, F, STR, F, T): self._mv_left,
            (STR, F, T, STR, F, STR, F, F): self._mv_left,
            (STR, F, T, STR, F, NVD, F, F): self._mv_left,
            (STR, F, F, INT, F, INT, F, T): self._mv_right,
            (STR, F, F, INT, F, INT, F, F): self._concat_left,
            (STR, F, F, INT, F, FLT, F, T): self._floatify_move_right,
            (STR, F, F, INT, F, FLT, F, F): self._concat_left,
            (STR, F, F, INT, F, STR, T, T): self._try_fl_mv_right_concat_left,
            (STR, F, F, INT, F, STR, T, F): self._concat_left,
            (STR, F, F, INT, F, STR, F, T): self._concat_left,
            (STR, F, F, INT, F, STR, F, F): self._concat_left,
            (STR, F, F, INT, F, NVD, F, F): self._concat_left,
            (STR, F, F, FLT, F, INT, F, T): self._try_intify_mv_right__concat_left,
            (STR, F, F, FLT, F, INT, F, F): self._concat_left,
            (STR, F, F, FLT, F, FLT, F, T): self._mv_right,
            (STR, F, F, FLT, F, FLT, F, F): self._concat_left,
            (STR, F, F, FLT, F, STR, T, T): self._try_fl_mv_right_concat_left,  # TODO: discuss
            (STR, F, F, FLT, F, STR, T, F): self._concat_left,
            (STR, F, F, FLT, F, STR, F, T): self._concat_left,  # TODO: discuss
            (STR, F, F, FLT, F, STR, F, F): self._concat_left,
            (STR, F, F, FLT, F, NVD, F, F): self._concat_left,
            (STR, F, F, STR, T, INT, F, T): self._concat_left,
            (STR, F, F, STR, T, INT, F, F): self._concat_left,
            (STR, F, F, STR, T, FLT, F, T): self._concat_left,
            (STR, F, F, STR, T, FLT, F, F): self._concat_left,
            (STR, F, F, STR, T, STR, T, T): self._try_fl_mv_right_concat_left,
            (STR, F, F, STR, T, STR, T, F): self._concat_left,
            (STR, F, F, STR, T, STR, F, T): self._concat_left,
            (STR, F, F, STR, T, STR, F, F): self._concat_left,
            (STR, F, F, STR, T, NVD, F, F): self._concat_left,
            (STR, F, F, STR, F, INT, F, T): self._concat_left,
            (STR, F, F, STR, F, INT, F, F): self._concat_left,
            (STR, F, F, STR, F, FLT, F, T): self._concat_left,
            (STR, F, F, STR, F, FLT, F, F): self._concat_left,
            (STR, F, F, STR, F, STR, T, T): self._try_fl_mv_right_concat_left,
            (STR, F, F, STR, F, STR, T, F): self._concat_left,
            (STR, F, F, STR, F, STR, F, T): self._concat_left,  # TODO: discuss
            (STR, F, F, STR, F, STR, F, F): self._concat_left,
            (STR, F, F, STR, F, NVD, F, F): self._concat_left,
            (NVD, F, F, INT, F, INT, F, T): self._mv_right,
            # (NVD, F, F, INT, F, INT, F, F): self.dummy,  # TODO: discuss
            (NVD, F, F, INT, F, FLT, F, T): self._floatify_move_right,
            (NVD, F, F, INT, F, STR, T, T): self._try_fl_mv_right,
            (NVD, F, F, INT, F, STR, F, T): self._mv_right,
            (NVD, F, F, INT, F, STR, F, F): self._concat_right,
            (NVD, F, F, FLT, F, INT, F, T): self._try_intify_mv_right,
            (NVD, F, F, FLT, F, FLT, F, T): self._mv_right,
            # (NVD, F, F, FLT, F, FLT, F, F): self.dummy,  # TODO: discuss
            (NVD, F, F, FLT, F, STR, T, T): self._try_fl_mv_right,
            (NVD, F, F, FLT, F, STR, F, T): self._mv_right,
            (NVD, F, F, FLT, F, STR, F, F): self._concat_right,
            (NVD, F, F, STR, T, STR, T, T): self._try_fl_mv_right,
            # (NVD, F, F, STR, T, STR, T, F): self.dummy,  # TODO: discuss
            (NVD, F, F, STR, T, STR, F, T): self._mv_right,
            (NVD, F, F, STR, T, STR, F, F): self._concat_right,
            (NVD, F, F, STR, F, STR, T, T): self._try_fl_mv_right,
            (NVD, F, F, STR, F, STR, F, T): self._mv_right,
            (NVD, F, F, STR, F, STR, F, F): self._concat_right
        }

        self._delimiter = delimiter
        self._threshold = threshold
        # this threshold determines the minimum portion of fixed length string
        # values (of a given length) that must exist to introduce a dedicated
        # fixed length string column TODO: make this configurable somehow
        self._len_threshold = 0.3
        # controls whether all adjacent string columns should be merged or
        # whether only sparse columns should be merged to their left neighbor
        # (if the neighbor col is also a str col with variable str length)
        # TODO: make this configurable somehow
        self._greedy_merge = True
        self._considered_lengths = [2, 3]
        self._max_token_str_len = len(self._null)
        self._max_line_tokens = 0
        self._token_col_types = []
        self._token_col_lengths = []

        # to keep track of the actual line number to write in the numpy array
        self._line_counter = 0

        # list of lists (i.e. pseudo 2d array) containing the actual line
        # tokens
        self._line_tokens = [[]]

    def add_line(self, line):
        """Takes an input line and splits it up to single tokens which are then
        added to self._line_tokens
        """
        tokens = line.split(self._delimiter)
        self._max_line_tokens = max(self._max_line_tokens, len(tokens))

        for token in tokens:
            if token == '':
                continue
            # update the max token str len stats
            self._max_token_str_len = max(self._max_token_str_len, len(token))

            # append empty line token list if necessary
            if self._line_counter >= len(self._line_tokens):
                    self._line_tokens.append([])

            # add token to line tokens
            self._line_tokens[self._line_counter].append(token)

        self._line_counter += 1

    def _create_array(self):
        """generates an initial numpy character array based on the stats
        collected from the input data
        """
        arr = np.chararray(
            (self._line_counter, self._max_line_tokens),
            self._max_token_str_len)
        for i in range(self._line_counter):
            num_tokens = len(self._line_tokens[i])
            arr_line = self._line_tokens[i] + \
                [self._null]*(self._max_line_tokens-num_tokens)
            arr[i] = arr_line
        return arr

    def _get_type(self, token):
        if token == self._null:
            token_type = self._null_type
        else:
            token_type = self._str

            try:
                float(token)
                token_type = self._float
            except ValueError:
                pass

            try:
                int(token)
                token_type = self._int
            except ValueError:
                pass

        return token_type

    def _col_has_non_fixed_len_str_vals(self, col):
        for value in col:
            if self._get_type(value) == self._str and \
                    len(value) not in self._considered_lengths:
                return True

        return False

    def _get_length_count(self, token_col, length):
        count = 0
        for token in token_col:
            if self._get_type(token) == self._str:
                if len(token) == length:
                    count += 1
        return count

    def _merge_cols(self, arr):
        arr_hash = hash(arr.tostring())

        while True:
            arr = self.__merge_cols(arr)

            new_arr_hash = hash(arr.tostring())
            if arr_hash != new_arr_hash:
                arr_hash = new_arr_hash
            else:
                break

        return arr

    def __merge_cols(self, arr):
        token_col_nr = arr.shape[1] - 1

        while token_col_nr > 0:

            # get neighbor column types
            type_left_col = self._token_col_types[token_col_nr-1]
            type_curr_col = self._token_col_types[token_col_nr]

            fixed_len_left_col = self._token_col_lengths[token_col_nr-1] > 0
            fixed_len_curr_col = self._token_col_lengths[token_col_nr] > 0

            if token_col_nr == arr.shape[1]-1:
                # we're in the rightmost  column
                type_rght_col = self._invalid
                fixed_len_rght_col = False
            else:
                type_rght_col = self._token_col_types[token_col_nr+1]
                fixed_len_rght_col = \
                    self._token_col_lengths[token_col_nr+1] > 0

            line_counter = 0
            while line_counter < arr.shape[0]:
                if arr[line_counter, token_col_nr] == self._null:
                    line_counter += 1
                    continue

                is_empty_left = arr[line_counter, token_col_nr-1] == self._null
                if type_rght_col == self._invalid:
                    is_empty_rght = False
                else:
                    is_empty_rght = \
                        arr[line_counter, token_col_nr+1] == self._null

                signature = (
                    type_left_col,
                    fixed_len_left_col,
                    is_empty_left,
                    type_curr_col,
                    fixed_len_curr_col,
                    type_rght_col,
                    fixed_len_rght_col,
                    is_empty_rght
                )
                fn = self._merge_cases.get(signature)
                if fn is not None and self._is_sparse(arr[:, token_col_nr]):
                    arr = fn(arr, line_counter, token_col_nr)

                line_counter += 1

            if self._is_empty(arr[:, token_col_nr]):
                arr = np.delete(arr, (token_col_nr), 1)
                self._token_col_lengths.pop(token_col_nr)
                self._token_col_types.pop(token_col_nr)
                token_col_nr -= 2
            else:
                token_col_nr -= 1

        return arr

    def _is_empty(self, col):
        num_non_null_vals = len(np.where(col != self._null)[0])
        return num_non_null_vals == 0

    def _find_combine_candidate_col(self, arr, tc_nr):
        # two cases:
        # 1) fstr col: find column with same str length
        # 2) non-str col: find column with same type
        if self._token_col_lengths[tc_nr] > 0:
            # 1)
            for c in range(tc_nr-1, -1, -1):
                if self._token_col_lengths[c] == \
                        self._token_col_lengths[tc_nr]:
                    return c
        elif self._token_col_types[tc_nr] != self._str:
            # 2)
            for c in range(tc_nr-1, -1, -1):
                if self._token_col_types[c] == self._token_col_types[tc_nr]:
                    return c

    def _has_index_clash(self, arr, col_idx1, col_idx2):
        col1 = arr[:, col_idx1]
        col2 = arr[:, col_idx2]
        # since masking doesn't work with char arrays... :(
        nn_idxs1 = np.where(col1 != b'NULL')[0]
        nn_idxs2 = np.where(col2 != b'NULL')[0]
        for idx in nn_idxs1:
            if idx in nn_idxs2:
                return True
        return False

    def _try_combine(self, arr, tc_nr, combine_col_idx):
        if not self._has_index_clash(arr, tc_nr, combine_col_idx):
            delta = tc_nr - combine_col_idx
            # insert delta-1 columns right to tc_nr
            new_cols = np.chararray((arr.shape[0], delta-1),
                                    self._max_token_str_len)
            new_cols.fill(self._null)

            l_arr = arr[:, :tc_nr+1]
            r_arr = arr[:, tc_nr+1:]

            arr = np.append(l_arr, new_cols, 1)
            arr = np.append(arr, r_arr, 1)

            for i in range(combine_col_idx+1, tc_nr):
                offset = i + delta
                col_type = self._token_col_types[i]
                self._token_col_types = self._token_col_types[:offset] + \
                    [col_type] + self._token_col_types[offset:]

                col_len = self._token_col_lengths[i]
                self._token_col_lengths = self._token_col_lengths[:offset] + \
                    [col_len] + self._token_col_lengths[offset:]

            line_idx = 0
            while line_idx < arr.shape[0]:
                value = arr[line_idx, combine_col_idx]
                if value != self._null:
                    c = combine_col_idx
                    while c < tc_nr:
                        offset = c + delta
                        arr[line_idx, offset] = arr[line_idx, c]
                        arr[line_idx, c] = self._null
                        c += 1

                line_idx += 1
        return arr

    def _merge_vstr_cols(self, arr):
        """
        - iterate over cols from right to left
        - 'sparse' vstr col --> check if left neighbor col is also vstr:
          - yes: concat left
        TODO: think about 'jumping over' type/fixed len cols
        """
        token_col_nr = arr.shape[1] - 1

        while token_col_nr > 0:
            # if left neighbor and considered col are var length str cols
            if self._token_col_types[token_col_nr] == self._str and \
                    self._token_col_types[token_col_nr-1] == self._str and \
                    self._token_col_lengths[token_col_nr] < 0 and \
                    self._token_col_lengths[token_col_nr-1] < 0:

                if self._greedy_merge or self._is_sparse(arr[:, token_col_nr]):
                    arr = self._merge_col_to_left(arr, token_col_nr)

                    self._token_col_types.pop(token_col_nr)
                    self._token_col_lengths.pop(token_col_nr)

                    arr = np.delete(arr, (token_col_nr), 1)
            token_col_nr -= 1

        return arr

    def _try_combine_cols(self, arr):
        token_col_nr = arr.shape[1] - 1

        border_idxs = [-1]
        while token_col_nr > 0:
            if self._is_empty(arr[:, token_col_nr]):
                token_col_nr -= 1
                continue

            if token_col_nr <= border_idxs[-1]:
                border_idxs.pop()

            if self._token_col_types[token_col_nr] != self._str or \
                    self._token_col_lengths[token_col_nr] > 0:
                cand_col_idx = self._find_combine_candidate_col(arr,
                                                                token_col_nr)
                if cand_col_idx is not None and \
                        not self._is_empty(arr[:, cand_col_idx]) and \
                        cand_col_idx > border_idxs[-1]:
                    old_num_cols = arr.shape[1]
                    arr = self._try_combine(arr, token_col_nr, cand_col_idx)
                    new_num_cols = arr.shape[1]
                    # move token col position behind new inserted columns
                    border_idxs.append(token_col_nr)
                    if (new_num_cols - old_num_cols) > 0:
                        token_col_nr += (new_num_cols - old_num_cols) + 1
            token_col_nr -= 1
        return arr

    def _merge_col_to_left(self, arr, token_col_nr):
        line_idx = 0

        while line_idx < arr.shape[0]:
            if arr[line_idx, token_col_nr] == self._null:
                line_idx += 1
                continue

            if arr[line_idx, token_col_nr-1] == self._null:
                # move to left
                arr[line_idx, token_col_nr-1] = arr[line_idx, token_col_nr]
                arr[line_idx, token_col_nr] = self._null
            else:
                # concat to left
                arr = self._concat(arr, line_idx, token_col_nr-1,
                                   token_col_nr, False)

            line_idx += 1

        return arr

    def _is_sparse(self, col):
        """Checks if a given column is sparse, i.e. whether the prevalent
        values are NULL values (with respect to the configured threshold)

        TODO: think about how this meaning of 'sparseness' relates to the
        self._len_threshold
        """
        num_null_vals = len(np.where(col == self._null)[0])
        num_vals = col.shape[0]
        return (num_null_vals / num_vals) >= self._threshold

    def _get_token_col_types(self, token_col):
        types = {}
        for token in token_col:

            token_type = self._get_type(token)

            if types.get(token_type) is None:
                types[token_type] = 1
            else:
                type_count = types[token_type]
                type_count += 1
                types[token_type] = type_count

        return types

    def _get_tc_col_type(self, tc_types):
        predom_type = None
        predom_type_count = 0
        whole_count = 0
        # strategy: if the portion of values being of predominat type is below
        # a certain threshold, try to generate pure string token columns to
        # move other types to the right. The assumption is, that with this
        # approach in the end more integer or float values will be aggregated
        # in one column

        # FIXME: move to __init__ and make configurable
        threshold = 0.8

        for tc_type in tc_types:
            whole_count += tc_types[tc_type]
            if tc_type == self._null_type:
                continue

            tc_type_count = tc_types[tc_type]
            if tc_type_count > predom_type_count:
                predom_type = tc_type
                predom_type_count = tc_type_count

        ratio = predom_type_count/whole_count
        if ratio < threshold and self._str in tc_types.keys():
            predom_type = self._str

        return predom_type

    def _get_neig_col_types(self, arr, token_col_nr):
        # check if there are values in the column to the right
        # yes --> valid; no --> invalid (i.e. we're in the last
        # token column)
        arr_col_num = arr.shape[1]
        if token_col_nr == (arr_col_num-1):
            right_col_type = self._invalid
        else:
            right_col_type = self._valid

        # get type of col to the left (invalid means, there is no
        # column to the left)
        if token_col_nr > 0:
            left_col_type = self._token_col_types[token_col_nr-1]
        else:
            left_col_type = self._invalid

        return left_col_type, right_col_type

    def _push_to_right(self, arr, line_idx, col_idx):
        is_rightmost_col = col_idx+1 == arr.shape[1]

        if not is_rightmost_col and arr[line_idx, col_idx+1] == self._null:
            arr[line_idx, col_idx+1] = arr[line_idx, col_idx]
        else:
            rightmost_idx = arr.shape[1] - 1
            if arr[line_idx, rightmost_idx] != self._null:
                new_col = np.chararray((arr.shape[0], 1),
                                       self._max_token_str_len)
                new_col.fill(self._null)
                arr = np.append(arr, new_col, 1)
                arr[line_idx, rightmost_idx+1] = arr[line_idx, rightmost_idx]

            c = rightmost_idx-1

            while c >= col_idx:
                # copy to the right
                arr[line_idx, c+1] = arr[line_idx, c]
                c -= 1

        arr[line_idx, col_idx] = self._null

        return arr

    def _mv_from_vstr_col(self, arr, tc_nr, l_type):
        # in case we're in the leftmost token column l_len is set to -1 to not
        # move to the left
        if tc_nr == 0:
            l_len = -1
        else:
            l_len = self._token_col_lengths[tc_nr-1]

        line_idx = 0
        while line_idx < arr.shape[0]:
            value = arr[line_idx, tc_nr]
            val_len = len(value)
            val_type = self._get_type(value)
            # move values with len in self._considered_lengths
            if value != self._null and (val_type != self._str or
                                        val_len in self._considered_lengths):
                # check if value can be moved to left
                if val_len == l_len and val_type == l_type and \
                        arr[line_idx, tc_nr-1] == self._null:
                    # move left
                    arr[line_idx, tc_nr-1] = value
                    arr[line_idx, tc_nr] = self._null
                else:
                    # push to right
                    arr = self._push_to_right(arr, line_idx, tc_nr)
            line_idx += 1

        return arr

    def _get_col_fixed_len(self, col):
        str_lens_counts = []
        has_non_str_vals = False
        for str_len in self._considered_lengths:
            str_lens_counts.append(0)

        for value in col:
            if value == self._null:
                continue
            if self._get_type(value) != self._str:
                has_non_str_vals = True
                continue
            else:
                val_len = len(value)
            for i in range(len(self._considered_lengths)):
                if val_len == self._considered_lengths[i]:
                    count = str_lens_counts[i]
                    count += 1
                    str_lens_counts[i] = count

        max_count = max(str_lens_counts)
        if max_count == 0:
            return None

        idx = str_lens_counts.index(max_count)

        str_lens_counts.pop(idx)
        if len(str_lens_counts) == 0 and not has_non_str_vals:
            # col is homogeneous w.r.t. the string length, i.e. there is no
            # 2nd most frequent string length
            return None

        return self._considered_lengths[idx]

    def _mv_from_fstr_col(self, arr, tc_nr, tc_len):
        """@param r_type: either self._valid or self._invalid
        """
        # TODO: add doc string

        # two cases:
        # 1) no insert check needed --> left col is not fstr --> push to right
        # 2) insert check left needed --> left col is fstr

        # in case we're in the leftmost token column l_len is set to -1 to not
        # move to the left
        if tc_nr == 0:
            l_len = -1
        else:
            l_len = self._token_col_lengths[tc_nr-1]

        if l_len < 0:
            # 1) ==============================================================
            line_idx = 0
            while line_idx < arr.shape[0]:
                # push non-null values with len != column length
                value = arr[line_idx, tc_nr]
                if value != self._null and len(value) != tc_len:
                    arr = self._push_to_right(arr, line_idx, tc_nr)
                line_idx += 1

        else:
            # 2) ==============================================================
            line_idx = 0
            while line_idx < arr.shape[0]:
                value = arr[line_idx, tc_nr]
                val_len = len(value)
                # move values with len != column length
                if value != self._null and val_len != tc_len:
                    # check if value can be moved to left
                    if val_len == l_len and \
                            arr[line_idx, tc_nr-1] == self._null:
                        # move left
                        arr[line_idx, tc_nr-1] = value
                        arr[line_idx, tc_nr] = self._null
                    else:
                        # push to right
                        arr = self._push_to_right(arr, line_idx, tc_nr)
                line_idx += 1

        return arr

    def _mv_from_str_col(self, arr, tc_number, l_type):
        # strategy: move all fixed length strings to the right, that in the end
        # more fixed length string will be aggregated in one column

        if self._col_has_non_fixed_len_str_vals(arr[:, tc_number]):
            # move all fixed len string values
            arr = self._mv_from_vstr_col(arr, tc_number, l_type)
            self._token_col_lengths.append(-1)
        else:
            # set one string length for this column and move all values with a
            # different string length
            str_len = self._get_col_fixed_len(arr[:, tc_number])
            if str_len is None:
                # there are no non-null values
                self._token_col_lengths.append(-1)
                return arr
            else:
                arr = self._mv_from_fstr_col(arr, tc_number, str_len)
                self._token_col_lengths.append(str_len)

        return arr

    def _mv_from_non_str_col(self, arr, tc_nr, tc_type, l_type):
        # TODO: doesn't really fit in here --> move!
        if tc_nr == 0:
            l_len = -1
        else:
            l_len = self._token_col_lengths[tc_nr-1]

        line_idx = 0
        while line_idx < arr.shape[0]:
            value = arr[line_idx, tc_nr]
            val_type = self._get_type(value)
            val_len = len(value)
            if val_type != tc_type:
                # try to move to left
                if l_type == val_type and l_len == val_len and \
                        arr[line_idx, tc_nr-1] == self._null:
                    arr[line_idx, tc_nr-1] = value
                    arr[line_idx, tc_nr] = self._null
                else:
                    arr = self._push_to_right(arr, line_idx, tc_nr)
            line_idx += 1
        self._token_col_lengths.append(-1)

        return arr

    def _mv_from_col(self, arr, tc_nr, tc_type, l_col_type):
        if tc_type == self._str:
            arr = self._mv_from_str_col(arr, tc_nr, l_col_type)
        else:
            arr = self._mv_from_non_str_col(arr, tc_nr, tc_type, l_col_type)

        return arr

    def _homogenize_token_col(self, arr, tc_nr, tc_types):
        tc_type = self._get_tc_col_type(tc_types)

        if tc_type is None:
            # column is empty
            return arr

        self._token_col_types.append(tc_type)

        l_col_type, r_col_type = self._get_neig_col_types(arr, tc_nr)
        # Now, tokens that are not of the predominant type are moved to the
        # left or right neighbor cells (except NULL tokens, of course)
        arr = self._mv_from_col(arr, tc_nr, tc_type, l_col_type)

        return arr

    def _homogenize(self, arr):
        token_col_nr = 0

        while token_col_nr < arr.shape[1]:
            tc_types = self._get_token_col_types(arr[:, token_col_nr])
            arr = self._homogenize_token_col(arr, token_col_nr, tc_types)

            if self._is_empty(arr[:, token_col_nr]):
                arr = np.delete(arr, (token_col_nr), 1)
                token_col_nr -= 1

            token_col_nr += 1

        return arr

    def get_data(self):
        """returns a homogenized version of the input column
        """
        arr = self._create_array()
        self._token_col_types = []
        arr = self._homogenize(arr)
        arr = self._merge_vstr_cols(arr)
        arr = self._try_combine_cols(arr)
        arr = self._merge_cols(arr)

        return arr
