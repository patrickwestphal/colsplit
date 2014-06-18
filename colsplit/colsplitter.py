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

    def dummy(self, arr, line_idx, col_idx):
        raise NotImplementedError("Just a dummy -- to be replaced")

    def _do_nothing(self, arr, line_idx, col_idx):
        pass

    def _move_cell_left(self, arr, line_idx, col_idx):
        arr[line_idx, col_idx-1] = arr[line_idx, col_idx]
        arr[line_idx, col_idx] = self._null

    def _try_intify_move_left(self, arr, line_idx, col_idx):
        """This method tries to 'cast' a float value to an integer and move it
        to the left neighbor cell
        """
        value = arr[line_idx, col_idx]
        # since the actual input string was detected to be a float, there can
        # only be one dot
        nonfrac, frac = value.split('.')
        if frac == 0:
            # move to left
            arr[line_idx, col_idx-1] = nonfrac
            arr[line_idx, col_idx] = self._null

    def _try_intify_move_right(self, arr, line_idx, col_idx):
        """This method tries to 'cast' a float value to an integer and move it
        to the right neighbor cell
        """
        curr_val = arr[line_idx, col_idx]
        nonfrac, frac = curr_val.split('.')
        if frac == 0:
            arr[line_idx, col_idx+1] = nonfrac
            arr[line_idx, col_idx] = self._null

    def _move_cell_right(self, arr, line_idx, col_idx):
        arr[line_idx, col_idx+1] = arr[line_idx, col_idx]
        arr[line_idx, col_idx] = self._null

    def _try_strfy_fl_mv_right__try_intify_mv_left(self, arr, line_idx, 
                                                   col_idx):
        """This method is used in case there is an integer column on the left
        and a fixed string column on the right. Moreover the considered column
        is a float column and both, the left and right neighbor cells are
        empty. Thus it is
        1) first tried to move the float value to the str column. This only
           works if the str length of the str column mathches the float value
           string length.
        2) If not it is tried to 'cast' the float value to an integer
        TESTME
        """
        curr_val = arr[line_idx, col_idx]
        
        # 1)
        r_col_len = self._token_col_lengths[col_idx+1]
        if len(curr_val) == r_col_len:
            arr[line_idx, col_idx+1] = curr_val
            arr[line_idx, col_idx] = self._null
        else:
            # 2)
            nonfrac, frac = curr_val.split('.')
            if frac == 0:
                arr[line_idx, col_idx-1] = nonfrac
                arr[line_idx, col_idx] = self._null

    def _try_intify__concat_mv_right(self, arr , line_idx, col_idx):
        """This method is used in cases where there is an integer column on the
        left and a (non-fixed) string column on the right. Moreover the
        considered column is a flaot column, the left neighbor cell is empty
        and the right neighbor cell is not. Thus it is
        1) first tried to 'cast' the float value to an integer and move it to
           the left.
        2) If this does not work, the float value is concated (from the left)
           to the right neighbor cell
        TESTME
        """
        curr_val = arr[line_idx, col_idx]
        nonfrac, frac = curr_val.split('.')
        if frac == 0:
            arr[line_idx, col_idx-1] = nonfrac
            arr[line_idx, col_idx] = self._null
        else:
            r_val = arr[line_idx, col_idx+1]
            new_r_val = curr_val + ' ' + r_val
            arr[line_idx, col_idx+1] = new_r_val
            arr[line_idx, col_idx] = self._null

    def _try_intify_mv_right__try_fl_mv_left(self, arr, line_idx, col_idx):
        """used in case  fstr | float | int
        """
        curr_val = arr[line_idx, col_idx]
        nonfrac, frac = curr_val.split('.')
        if frac == 0:
            arr[line_idx, col_idx+1] = nonfrac
            arr[line_idx, col_idx] = self._null
        else:
            l_col_len = self._token_col_lengths[col_idx-1]

            if len(curr_val) == l_col_len:
                arr[line_idx, col_idx-1] = curr_val
                arr[line_idx, col_idx] = self._null

    def _try_intify_mv_right__mv_left(self, arr, line_idx, col_idx):
        """used in case  vstr (NULL) | float | int (NULL)
        """
        curr_val = arr[line_idx, col_idx]
        nonfrac, frac = curr_val.split('.')
        if frac == 0:
            arr[line_idx, col_idx+1] = nonfrac
            arr[line_idx, col_idx] = self._null
        else:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null

    def _try_intify_mv_right__conc_left(self, arr, line_idx, col_idx):
        """used in case  vstr (NOT NULL) | float | int (NULL)
        """
        curr_val = arr[line_idx, col_idx]
        nonfrac, frac = curr_val.split('.')

        if frac == 0:
            arr[line_idx, col_idx+1] = nonfrac
            arr[line_idx, col_idx] = self._null
        else:
            l_neigh_val = arr[line_idx, col_idx-1]
            new_l_val = l_neigh_val + ' ' + curr_val
            arr[line_idx, col_idx-1] = new_l_val
            arr[line_idx, col_idx] = self._null

    def _try_fl_move_right(self, arr, line_idx, col_idx):
        """This method is used in cases where the considered column is of
        arbitrary type with a right neighbor being a string column. Since the
        right neighbor only contains fixed strings, it is checked whether the
        currently considered cell value has a suitable string length and could
        be moved to the empty right neighbor cell
        """
        curr_val = arr[line_idx, col_idx]
        r_col_len = self._token_col_lengths[col_idx+1]
        
        if len(curr_val) == r_col_len:
            arr[line_idx, col_idx+1] = curr_val
            arr[line_idx, col_idx] = self._null

    def _try_fl_move_left(self, arr, line_idx, col_idx):
        """This method is used in cases where the considered column is of
        arbitrary type with a left neighbor being a string column. Since the
        left neighbor only contains fixed strings, it is checked whether the
        currently considered cell value has a suitable string length and could
        be moved to the empty left neighbor cell
        """
        curr_val = arr[line_idx, col_idx]
        l_col_len = self._token_col_lengths[col_idx-1]

        if len(curr_val) == l_col_len:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null

    def _try_fl_move(self, arr, line_idx, col_idx):
        """This method is used in cases where the considered column is of
        arbitrary type with a left and right neighbor being a string column.
        Since the left and right neighbor only contain fixed strings, it is
        checked whether the currently considered cell value has a suitable
        string length and could be moved to on of the empty left neighbor cells
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

    def _try_fl_mv_left__floatify_mv_right(self, arr, line_idx, col_idx):
        """used in case of  fstr | int | float
        """
        curr_val = arr[line_idx, col_idx]
        l_col_len = self._token_col_lengths[col_idx-1]

        if len(curr_val) == l_col_len:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null
        else:
            new_r_val = curr_val + '.0'
            arr[line_idx, col_idx+1] = new_r_val
            arr[line_idx, col_idx] = self._null

    def _try_fl_mv_left__mv_right(self, arr, line_idx, col_idx):
        """used in case of fstr (NULL) | str | vstr (NULL)
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

    def _try_fl_mv_left__conc_right(self, arr, line_idx, col_idx):
        """used in case of fstr (NULL) | str | vstr (NOT NULL)
        """
        # try to move to left
        curr_val = arr[line_idx, col_idx]
        l_col_len = self._token_col_lengths[col_idx-1]

        if len(curr_val) == l_col_len:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null

        else:
            # concat to right neighbor
            r_neigh_val = arr[line_idx, col_idx+1]
            new_r_val = curr_val + ' ' + r_neigh_val
            arr[line_idx, col_idx+1] = new_r_val
            arr[line_idx, col_idx] = self._null

    def _try_fl_mv_right__mv_left(self, arr, line_idx, col_idx):
        """used in case of vstr (NULL) | <type> | fstr (NULL)
        """
        curr_val = arr[line_idx, col_idx]
        r_col_len = self._token_col_lengths[col_idx+1]

        if len(curr_val) == r_col_len:
            arr[line_idx, col_idx+1] = curr_val
            arr[line_idx, col_idx] = self._null

        else:
            arr[line_idx, col_idx-1] = curr_val
            arr[line_idx, col_idx] = self._null

    def _try_fl_mv_right__conc_left(self, arr, line_idx, col_idx):
        """used in case of  vstr (NOT NULL) | <type> | fstr (NULL)
        """
        curr_val = arr[line_idx, col_idx]
        r_col_len = self._token_col_lengths[col_idx+1]

        if len(curr_val) == r_col_len:
            arr[line_idx, col_idx+1] = curr_val
            arr[line_idx, col_idx] = self._null

        else:
            l_neigh_val = arr[line_idx, col_idx-1]
            new_l_val = l_neigh_val  + ' ' + curr_val
            arr[line_idx, col_idx-1] = new_l_val
            arr[line_idx, col_idx] = self._null

    def _concat_right(self, arr, line_idx, col_idx):
        """used in case the considered column is sparse and has a non-fixed str
        column right neighbor
        """
        curr_val = arr[line_idx, col_idx]
        r_neigh_val = arr[line_idx, col_idx+1]
        new_val = curr_val + ' ' + r_neigh_val
        arr[line_idx, col_idx+1] = new_val
        arr[line_idx, col_idx] = self._null

    def _concat_left(self, arr, line_idx, col_idx):
        """used in case the considered column is sparse and has a non-fixed str
        column left neighbor
        """
        curr_val = arr[line_idx, col_idx]
        l_neigh_val = arr[line_idx, col_idx-1]
        new_l_val = l_neigh_val + ' ' + curr_val
        arr[line_idx, col_idx-1] = new_l_val
        arr[line_idx, col_idx] = self._null

    def _floatify_move_right(self, arr , line_idx, col_idx):
        """Used in case a value from a sparse int column has an empty float
        cell neighbor
        """
        curr_val = arr[line_idx, col_idx]
        new_r_val = curr_val + '.0'
        arr[line_idx, col_idx+1] = new_r_val
        arr[line_idx, col_idx] = self._null

    def _floatify_move_left(self, arr, line_idx, col_idx):
        """used in case a value from a sparse int column has an empty float
        cell neighbor
        """
        curr_val = arr[line_idx, col_idx]
        new_l_val = curr_val + '.0'
        arr[line_idx, col_idx-1] = new_l_val
        arr[line_idx, col_idx] = self._null

    def __init__(self, delimiter=' ', threshold=0.7):
        
        # TODO: find default action

        # 0 --> type of the column to the left
        # 1 --> has the column to the left a fixed string length?
        # 2 --> is the left neighbor cell empty?
        # 3 --> type of the considered column
        # 4 --> has the considered column a fixed string length?
        # 5 --> is the considered column sparse?
        # 6 --> type of the column to the right
        # 7 --> has the column to the righ a fixed string length?
        # 8 --> is the left neighbor cell empty?
        self._merge_cases = {
            # 0000 - 0383 --> invalid
            # 0384 - 0415 --> invalid
            # 0416 - 0417 --> invalid
            (self._int, False, True, self._int, False, True,
             self._int, False, True): self._move_cell_left,  # 0418: left cell
                                                    # w/ same type and empty
            (self._int, False, True, self._int, False, True,
             self._int, False, False): self._move_cell_left,  # 0419: see above
            # 0420 - 0421 --> invalid
            (self._int, False, True, self._int, False, True,
             self._float, False, True): self._move_cell_left,  # 0422: left
                                                    # cell w/ same type & empty
            (self._int, False, True, self._int, False, True,
             self._float, False, False): self._move_cell_left,  # 0423: see
                                                                # above
            (self._int, False, True, self._int, False, True,
             self._str, True, True): self._move_cell_left,  # 0424: see above
            (self._int, False, True, self._int, False, True,
             self._str, True, False): self._move_cell_left,  # 0425: see above
            (self._int, False, True, self._int, False, True,
             self._str, False, True): self._move_cell_left,  # 0426: see above
            (self._int, False, True, self._int, False, True,
             self._str, False, False): self._move_cell_left,  # 0427: see above
            # 0429 - 0430 --> invalid
            (self._int, False, True, self._int, False, True,
             self._invalid, False, True): self._move_cell_left,  # 0434: left
                                                    # cell w/ same type & empty
            # 0435 --> invalid
            (self._int, False, True, self._int, False, True,
             self._invalid, False, False): self._move_cell_left,  # 0435: left
                                                    # cell w/ same type & empty
            (self._int, False, True, self._float, False, True,
             self._int, False, True): self._try_intify_move_left,  # 0486: left
                                                    # & right cell w/ different
                                                    # type -> try to align &
                                                    # move to empty left cell
            (self._int, False, True, self._float, False, True,
             self._int, False, False): self._try_intify_move_left,  # 0487: see
                                                                    # above
            # 0488 - 0489 --> invalid
            (self._int, False, True, self._float, False, True,
             self._float, False, True): self._move_cell_right,  # 0490: right
                                                    # cell w/ same type & empty
            (self._int, False, True, self._float, False, True,
             self._float, False, False): self._try_intify_move_left,  # 0491:
                                                    # right cell with same type
                                                    # but not empty --> try to
                                                    # move to left
            (self._int, False, True, self._float, False, True, self._str,
             True, True): self._try_strfy_fl_mv_right__try_intify_mv_left,
                                                    # 0492: int | float | fstr
                                                    # if len suits, move to
                                                    # right; else try to intify
                                                    # and move to left
            (self._int, False, True, self._float, False, True,
             self._str, True, False): self._try_intify_move_left,  # 0493:
                                                    # int | float | fstr
                                                    # right neighbor not empty
                                                    # --> try to move to left
            (self._int, False, True, self._float, False, True,
             self._str, False, True): self._move_cell_right,  # 0494:
                                                    # int | float | vstr
                                                    # right neighbor empty -->
                                                    # mv to right
            (self._int, False, True, self._float, False, True,
             self._str, False, False): self._try_intify__concat_mv_right,
                                                    # 0495: int | float | vstr
                                                    # try to intify & mv left,
                                                    # then concat to right
                                                    # neighbor
            # 0496 - 0498 --> invalid
            (self._int, False, True, self._float, False, True,
             self._invalid, False, False): self._try_intify_move_left,  # 0499:
                                                    # ... | int | float
                                                    # no right col; try to
                                                    # intify & mv left
            # 0500 - 0501 --> invalid
            # 0502 - 0502 --> do nothing (not sparse)
            # 0504 - 0505 --> invalid
            # 0506 - 0511 --> do nothing (not sparse)
            # 0512 - 0514 --> invalid
            # 0515 --> do nothing (not sparse)
            # 0516 - 0523: type | str | type; str sparse --> do nothing
            # 0524: int | fstr | fstr (NOT NULL) --> do nothing
            (self._int, False, True, self._str, True, True,
             self._str, True, False): self._try_fl_move_right,  # 0525
            (self._int, False, True, self._str, True, True,
             self._str, False, True): self._concat_right,
            (self._int, False, True, self._str, True, True,
             self._str, False, False): self._move_cell_right,  # 0527
            # 0528 - 0530 --> invalid
            # 0531 --> do nothing
            # 0532 - 0533 --> nothing to do
            # 0534 - 0547 --> nothing to do (not sparse or invalid)
            # 0548 - 0549 --> invalid
            # 0550 - 0551 --> nothing to do
            # 0552 - 0553 --> invalid
            # 0554 - 0555 --> nothing to do
            (self._int, False, True, self._str, False, True,
             self._str, True, True): self._try_fl_move_right,
            # 0557 --> nothing to do
            (self._int, False, True, self._str, False, True,
             self._str, False, True): self._move_cell_right,
            (self._int, False, True, self._str, False, True,
             self._str, False, False): self._concat_right,  # 0559
            # 0560 - 0562 --> invalid
            # 0563 - 0579 --> nothing to do
            # 0580 - 0613--> invalid
            (self._int, False, False, self._int, False, True,
             self._int, False, True): self._move_cell_right,
            # 0615 --> nothing to do
            # 0616 - 0617 --> invalid
            (self._int, False, False, self._int, False, True,
             self._float, False, True): self._floatify_move_right,
            # 0619 --> nothing to do
            (self._int, False, False, self._int, False, True,
             self._str, True, True): self._try_fl_move_right,
            # 0621 --> nothing to do
            (self._int, False, False, self._int, False, True,
             self._str, False, True): self._move_cell_right,
            (self._int, False, False, self._int, False, True,
             self._str, False, False): self._concat_right,  # 0623
            # 0624 - 0626 --> invalid
            # 0627 --> nothing to do
            # 0628 - 0629 --> invalid
            # 0630 - 0643 --> nothing to do (not sparse/invalid)
            # 0645 - 0675 --> invalid
            # 0676 - 0677 --> invalid
            (self._int, False, False, self._float, False, True,
             self._int, False, True): self._try_intify_move_right,
            # 0679 --> nothing to do
            # 0680 - 0681 --> invalid
            (self._int, False, False, self._float, False, True,
             self._float, False, True): self._move_cell_right,
            # 0683 --> nothing to do
            (self._int, False, False, self._float, False, True,
             self._str, True, True): self._try_fl_move_right,
            # 0685 --> nothing to do
            (self._int, False, False, self._float, False, True,
             self._str, False, True): self._move_cell_right,
            (self._int, False, False, self._float, False, True,
             self._str, False, False): self._concat_right,  # 0687
            # 0688 - 0690 --> invalid
            # 0691 --> nothing to do
            # 0692 - 0707 --> nothing to do (not sparse/invalid)
            (self._int, False, False, self._str, True, True, self._str, True, True): self._try_fl_move_right,
            (self._int, False, False, self._str, True, True, self._str, False, True): self._move_cell_right,
            (self._int, False, False, self._str, True, True, self._str, False, False): self._concat_right,  # 0719
            (self._int, False, False, self._str, False, True, self._str, True, True): self._try_fl_move_right,
            (self._int, False, False, self._str, False, True, self._str, False, True): self._move_cell_right,
            (self._int, False, False, self._str, False, True, self._str, False, False): self._concat_right,  # 0751


            (self._float, False, True, self._int, False, True, self._int, False, True): self._move_cell_right,
            (self._float, False, True, self._int, False, True, self._int, False, False): self._floatify_move_left,  # 1191
            (self._float, False, True, self._int, False, True, self._float, False, True): self._floatify_move_left,
            (self._float, False, True, self._int, False, True, self._float, False, False): self._floatify_move_left,  # 1195
            (self._float, False, True, self._int, False, True, self._str, True, True): self._floatify_move_left,
            (self._float, False, True, self._int, False, True, self._str, True, False): self._floatify_move_left,  # 1197
            (self._float, False, True, self._int, False, True, self._str, False, True): self._floatify_move_left,  # TODO: discuss
            (self._float, False, True, self._int, False, True, self._str, False, False): self._floatify_move_left,  # 1199
            (self._float, False, True, self._float, False, True, self._int, False, True): self._move_cell_left,
            (self._float, False, True, self._float, False, True, self._int, False, False): self._move_cell_left,  # 1255
            (self._float, False, True, self._float, False, True, self._float, False, True): self._move_cell_left,
            (self._float, False, True, self._float, False, True, self._float, False, False): self._move_cell_left,  # 1259
            (self._float, False, True, self._float, False, True, self._str, True, True): self._move_cell_left,
            (self._float, False, True, self._float, False, True, self._str, True, False): self._move_cell_left,  # 1261
            (self._float, False, True, self._float, False, True, self._str, False, True): self._move_cell_left,
            (self._float, False, True, self._float, False, True, self._str, False, False): self._move_cell_left,  # 1263
            (self._float, False, True, self._str, True, True, self._str, True, True): self._try_fl_move_right,
            (self._float, False, True, self._str, True, True, self._str, False, True): self._move_cell_right,
            (self._float, False, True, self._str, True, True, self._str, False, False): self._concat_right,  # 1295
            (self._float, False, True, self._str, False, True, self._str, True, True): self._try_fl_move_right,
            (self._float, False, True, self._str, False, True, self._str, False, True): self._move_cell_right,
            (self._float, False, True, self._str, False, True, self._str, False, False): self._concat_right,  # 1327

            (self._float, False, False, self._int, False, True, self._int, False, True): self._move_cell_right,
            (self._float, False, False, self._int, False, True, self._float, False, True): self._floatify_move_right,
            (self._float, False, False, self._int, False, True, self._str, True, True): self._try_fl_move_right,
            (self._float, False, False, self._int, False, True, self._str, False, True): self._move_cell_right,
            (self._float, False, False, self._int, False, True, self._str, False, False): self._concat_right,  # 1391
            (self._float, False, False, self._float, False, True, self._int, False, True): self._try_intify_move_right,
            (self._float, False, False, self._float, False, True, self._float, False, True): self._move_cell_right,
            (self._float, False, False, self._float, False, True, self._str, True, True): self._try_fl_move_right,
            (self._float, False, False, self._float, False, True, self._str, False, True): self._move_cell_right,
            (self._float, False, False, self._float, False, True, self._str, False, False): self._concat_right,  # 1455
            (self._float, False, False, self._str, True, True, self._str, True, True): self._try_fl_move_right,
            (self._float, False, False, self._str, True, True, self._str, False, True): self._move_cell_right,
            (self._float, False, False, self._str, True, True, self._str, False, False): self._concat_right,  # 1487
            (self._float, False, False, self._str, False, True, self._str, True, True): self._try_fl_move_right,
            (self._float, False, False, self._str, False, True, self._str, False, True): self._move_cell_right,
            (self._float, False, False, self._str, False, True, self._str, False, False): self._concat_right,  # 1519


            (self._str, True, True, self._int, False, True, self._int, False, True): self._move_cell_right,
            (self._str, True, True, self._int, False, True, self._int, False, False): self._try_fl_move_left,  # 1575
            (self._str, True, True, self._int, False, True, self._float, False, True): self._try_fl_mv_left__floatify_mv_right,
            (self._str, True, True, self._int, False, True, self._float, False, False): self._try_fl_move_left,  # 1579
            (self._str, True, True, self._int, False, True, self._str, True, True): self._try_fl_move,
            (self._str, True, True, self._int, False, True, self._str, True, False): self._try_fl_move_left,  # 1581
            (self._str, True, True, self._int, False, True, self._str, False, True): self._move_cell_right, # TODO: discuss
            (self._str, True, True, self._int, False, True, self._str, False, False): self._concat_right,  # 1583  # TODO: discuss
            (self._str, True, True, self._float, False, True, self._int, False, True): self._try_intify_mv_right__try_fl_mv_left,  # TODO: discuss
            (self._str, True, True, self._float, False, True, self._int, False, False): self._try_fl_move_left,  # 1639
            (self._str, True, True, self._float, False, True, self._float, False, True): self._move_cell_right,
            (self._str, True, True, self._float, False, True, self._float, False, False): self._try_fl_move_left,  # 1643
            (self._str, True, True, self._float, False, True, self._str, True, True): self._try_fl_move,
            (self._str, True, True, self._float, False, True, self._str, True, False): self._try_fl_move_left,  # 1645
            (self._str, True, True, self._float, False, True, self._str, False, True): self._concat_right,  # TODO: discuss
            (self._str, True, True, self._float, False, True, self._str, False, False): self._try_fl_move_left,  # 1647
            (self._str, True, True, self._float, False, True, self._invalid, False, False): self._try_fl_move_left,  # 1651
            (self._str, True, True, self._str, True, True, self._int, False, True): self._try_fl_move_left,
            (self._str, True, True, self._str, True, True, self._int, False, False): self._try_fl_move_left,  # 1671
            (self._str, True, True, self._str, True, True, self._float, False, True): self._try_fl_move_left,
            (self._str, True, True, self._str, True, True, self._float, False, False): self._try_fl_move_left,  # 1675
            (self._str, True, True, self._str, True, True, self._str, True, True): self._try_fl_move,
            (self._str, True, True, self._str, True, True, self._str, True, False): self._try_fl_move_left,  # 1677
            (self._str, True, True, self._str, True, True, self._str, False, True): self._try_fl_mv_left__mv_right,
            (self._str, True, True, self._str, True, True, self._str, False, False): self._try_fl_mv_left__conc_right,  # 1679
            (self._str, True, True, self._str, True, True, self._invalid, False, False): self._try_fl_move_left,  # 1683
            (self._str, True, True, self._str, False, True, self._int, False, True): self._try_fl_move_left,
            (self._str, True, True, self._str, False, True, self._int, False, False): self._try_fl_move_left,  # 1703
            (self._str, True, True, self._str, False, True, self._float, False, True): self._try_fl_move_left,
            (self._str, True, True, self._str, False, True, self._float, False, False): self._try_fl_move_left,  # 1707
            (self._str, True, True, self._str, False, True, self._str, True, True): self._try_fl_move,
            (self._str, True, True, self._str, False, True, self._str, True, False): self._try_fl_move_left,  # 1709
            (self._str, True, True, self._str, False, True, self._str, False, True): self._try_fl_mv_left__mv_right,
            (self._str, True, True, self._str, False, True, self._str, False, False): self._try_fl_mv_left__conc_right,  # 1711
            (self._str, True, True, self._str, False, True, self._invalid, False, False): self._try_fl_move_left,  # 1715

            (self._str, True, False, self._int, False, True, self._int, False, True): self._move_cell_right,
            (self._str, True, False, self._int, False, True, self._float, False, True): self._floatify_move_right,
            (self._str, True, False, self._int, False, True, self._str, True, True): self._try_fl_move_right,
            (self._str, True, False, self._int, False, True, self._str, False, True): self._move_cell_right,
            (self._str, True, False, self._int, False, True, self._str, False, False): self._concat_right,  # 1775
            (self._str, True, False, self._float, False, True, self._int, False, True): self._try_intify_move_right,
            (self._str, True, False, self._float, False, True, self._float, False, True): self._move_cell_right,
            (self._str, True, False, self._float, False, True, self._str, True, True): self._try_fl_move_right,
            (self._str, True, False, self._float, False, True, self._str, False, True): self._move_cell_right,
            (self._str, True, False, self._float, False, True, self._str, False, False): self._concat_right,  # 1839
            (self._str, True, False, self._str, True, True, self._str, True, True): self._try_fl_move_right,
            (self._str, True, False, self._str, True, True, self._str, False, True): self._move_cell_right,
            (self._str, True, False, self._str, True, True, self._str, False, False): self._concat_right,  # 1871
            (self._str, True, False, self._str, False, True, self._str, True, True): self._try_fl_move_right,
            (self._str, True, False, self._str, False, True, self._str, False, True): self._move_cell_right,
            (self._str, True, False, self._str, False, True, self._str, False, False): self._concat_right,  # 1903

            (self._str, False, True, self._int, False, True, self._int, False, True): self._move_cell_right,
            (self._str, False, True, self._int, False, True, self._int, False, False): self._move_cell_left,  # 1959
            (self._str, False, True, self._int, False, True, self._float, False, True): self._floatify_move_right,
            (self._str, False, True, self._int, False, True, self._float, False, False): self._move_cell_left,  # 1963
            (self._str, False, True, self._int, False, True, self._str, True, True): self._move_cell_left,  # TODO: discuss
            (self._str, False, True, self._int, False, True, self._str, True, False): self._move_cell_left,  # 1965
            (self._str, False, True, self._int, False, True, self._str, False, True): self._move_cell_left,
            (self._str, False, True, self._int, False, True, self._str, False, False): self._move_cell_left,  # 1967
            (self._str, False, True, self._int, False, True, self._invalid, False, False): self._move_cell_left,  # 1971
            (self._str, False, True, self._float, False, True, self._int, False, True): self._try_intify_mv_right__mv_left,
            (self._str, False, True, self._float, False, True, self._int, False, False): self._move_cell_left,  # 2023
            (self._str, False, True, self._float, False, True, self._float, False, True): self._move_cell_right,
            (self._str, False, True, self._float, False, True, self._float, False, False): self._move_cell_left,  # 2027
            (self._str, False, True, self._float, False, True, self._str, True, True): self._move_cell_left,  # TODO: discuss
            (self._str, False, True, self._float, False, True, self._str, True, False): self._move_cell_left,  # 2029
            (self._str, False, True, self._float, False, True, self._str, False, True): self._move_cell_left,
            (self._str, False, True, self._float, False, True, self._str, False, False): self._move_cell_left,  # 2031
            (self._str, False, True, self._float, False, True, self._invalid, False, False): self._move_cell_left,  # 2035
            (self._str, False, True, self._str, True, True, self._int, False, True): self._move_cell_left,
            (self._str, False, True, self._str, True, True, self._int, False, False): self._move_cell_left,  # 2055
            (self._str, False, True, self._str, True, True, self._float, False, True): self._move_cell_left,
            (self._str, False, True, self._str, True, True, self._float, False, False): self._move_cell_left,  # 2059
            (self._str, False, True, self._str, True, True, self._str, True, True): self._try_fl_mv_right__mv_left,
            (self._str, False, True, self._str, True, True, self._str, True, False): self._move_cell_left,  # 2061
            (self._str, False, True, self._str, True, True, self._str, False, True): self._move_cell_left,
            (self._str, False, True, self._str, True, True, self._str, False, False): self._move_cell_left,  # 2063
            (self._str, False, True, self._str, True, True, self._invalid, False, False): self._move_cell_left,  # 2067
            (self._str, False, True, self._str, False, True, self._int, False, True): self._move_cell_left,
            (self._str, False, True, self._str, False, True, self._int, False, False): self._move_cell_left,  # 2087
            (self._str, False, True, self._str, False, True, self._float, False, True): self._move_cell_left,
            (self._str, False, True, self._str, False, True, self._float, False, False): self._move_cell_left,  # 2091
            (self._str, False, True, self._str, False, True, self._str, True, True): self._try_fl_mv_right__mv_left,
            (self._str, False, True, self._str, False, True, self._str, True, False): self._move_cell_left,  # 2093
            (self._str, False, True, self._str, False, True, self._str, False, True): self._move_cell_left,
            (self._str, False, True, self._str, False, True, self._str, False, False): self._move_cell_left,  # 2095
            (self._str, False, True, self._str, False, True, self._invalid, False, False): self._move_cell_left,  # 2099

            (self._str, False, False, self._int, False, True, self._int, False, True): self._move_cell_right,
            (self._str, False, False, self._int, False, True, self._int, False, False): self._concat_left,  # 2151
            (self._str, False, False, self._int, False, True, self._float, False, True): self._floatify_move_right,
            (self._str, False, False, self._int, False, True, self._float, False, False): self._concat_left,  # 2155
            (self._str, False, False, self._int, False, True, self._str, True, True): self._try_fl_mv_right__conc_left,
            (self._str, False, False, self._int, False, True, self._str, True, False): self._concat_left,  # 2157
            (self._str, False, False, self._int, False, True, self._str, False, True): self._concat_left,  # TODO: discuss
            (self._str, False, False, self._int, False, True, self._str, False, False): self._concat_left,  # 2159
            (self._str, False, False, self._int, False, True, self._invalid, False, False): self._concat_left,  # 2163
            (self._str, False, False, self._float, False, True, self._int, False, True): self._try_intify_mv_right__conc_left,
            (self._str, False, False, self._float, False, True, self._int, False, False): self._concat_left,  # 2215
            (self._str, False, False, self._float, False, True, self._float, False, True): self._move_cell_right,
            (self._str, False, False, self._float, False, True, self._float, False, False): self._concat_left,  # 2219
            (self._str, False, False, self._float, False, True, self._str, True, True): self._try_fl_mv_right__conc_left,  # TODO: discuss
            (self._str, False, False, self._float, False, True, self._str, True, False): self._concat_left,  # 2221
            (self._str, False, False, self._float, False, True, self._str, False, True): self._concat_left,  # TODO: discuss
            (self._str, False, False, self._float, False, True, self._str, False, False): self._concat_left,  # 2223
            (self._str, False, False, self._float, False, True, self._invalid, False, False): self._concat_left,  # 2227
            (self._str, False, False, self._str, True, True, self._int, False, True): self._concat_left,
            (self._str, False, False, self._str, True, True, self._int, False, False): self._concat_left,  # 2247
            (self._str, False, False, self._str, True, True, self._float, False, True): self._concat_left,
            (self._str, False, False, self._str, True, True, self._float, False, False): self._concat_left,  # 2251
            (self._str, False, False, self._str, True, True, self._str, True, True): self._try_fl_mv_right__conc_left,
            (self._str, False, False, self._str, True, True, self._str, True, False): self._concat_left,  # 2253
            (self._str, False, False, self._str, True, True, self._str, False, True): self._concat_left,
            (self._str, False, False, self._str, True, True, self._str, False, False): self._concat_left,  # 2255
            (self._str, False, False, self._str, True, True, self._invalid, False, False): self._concat_left,  # 2259
            (self._str, False, False, self._str, False, True, self._int, False, True): self._concat_left,
            (self._str, False, False, self._str, False, True, self._int, False, False): self._concat_left,  # 2279
            (self._str, False, False, self._str, False, True, self._float, False, True): self._concat_left,
            (self._str, False, False, self._str, False, True, self._float, False, False): self._concat_left,  # 2283
            (self._str, False, False, self._str, False, True, self._str, True, True): self._try_fl_mv_right__conc_left,
            (self._str, False, False, self._str, False, True, self._str, True, False): self._concat_left,  # 2285
            (self._str, False, False, self._str, False, True, self._str, False, True): self._concat_left,  # TODO: discuss
            (self._str, False, False, self._str, False, True, self._str, False, False): self._concat_left,  # 2287
            (self._str, False, False, self._str, False, True, self._invalid, False, False): self._concat_left,  # 2291


            (self._invalid, True, True, self._str, True, True, self._str, True, True): self._try_fl_move_right,
            # (self._invalid, True, True, self._str, True, True, self._str, True, False): self.dummy,  # 2445  # TODO: discuss
            (self._invalid, True, True, self._str, True, True, self._str, False, True): self._move_cell_right,
            (self._invalid, True, True, self._str, True, True, self._str, False, False): self._concat_right,  # 2447
            (self._invalid, True, True, self._str, False, True, self._str, True, True): self._try_fl_move_right,
            (self._invalid, True, True, self._str, False, True, self._str, False, True): self._move_cell_right(),
            (self._invalid, True, True, self._str, False, True, self._str, False, False): self._concat_right,  # 2479


            (self._invalid, False, False, self._int, False, True, self._int, False, True): self._move_cell_right,
            # (self._invalid, False, False, self._int, False, True, self._int, False, False): self.dummy,  # 2919  # TODO: discuss
            (self._invalid, False, False, self._int, False, True, self._float, False, True): self._floatify_move_right,
            (self._invalid, False, False, self._int, False, True, self._str, True, True): self._try_fl_move_right,
            (self._invalid, False, False, self._int, False, True, self._str, False, True): self._move_cell_right,
            (self._invalid, False, False, self._int, False, True, self._str, False, False): self._concat_right,  # 2927
            (self._invalid, False, False, self._float, False, True, self._int, False, True): self._try_intify_move_right,
            (self._invalid, False, False, self._float, False, True, self._float, False, True): self._move_cell_right,
            # (self._invalid, False, False, self._float, False, True, self._float, False, False): self.dummy,  # 2987  # TODO: discuss
            (self._invalid, False, False, self._float, False, True, self._str, True, True): self._try_fl_move_right,
            (self._invalid, False, False, self._float, False, True, self._str, False, True): self._move_cell_right,
            (self._invalid, False, False, self._float, False, True, self._str, False, False): self._concat_right,  # 2991
            (self._invalid, False, False, self._str, True, True, self._str, True, True): self._try_fl_move_right,
            # (self._invalid, False, False, self._str, True, True, self._str, True, False): self.dummy,  # 3021  # TODO: discuss
            (self._invalid, False, False, self._str, True, True, self._str, False, True): self._move_cell_right,
            (self._invalid, False, False, self._str, True, True, self._str, False, False): self._concat_right,  # 3023
            (self._invalid, False, False, self._str, False, True, self._str, True, True): self._try_fl_move_right,
            (self._invalid, False, False, self._str, False, True, self._str, False, True): self._move_cell_right,
            (self._invalid, False, False, self._str, False, True, self._str, False, False): self._concat_right,  # 3055
        }

        self._delimiter = delimiter
        self._threshold = threshold
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

    def _get_types(self, token_col):
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

    def _move_from_null_col(self, arr, token_col_nr, l_col_type, r_col_type):
        """This method moves all tokens of a sparse token column to the
        neighbor columns, if possible. First it is tried to move tokens to the
        left neighbor column. This only works if the type of the token matches
        the type of the left neighbor column and the corresponding token cell
        is empty. In all other cases it is tried to move tokens to the right.
        In case the right neighbor cell is not empty, the whole right 'sub
        line' has to be moved after introducing a new column on the rightmost
        position.
        In case, the considered token column is the last, i.e. rightmost, no
        tokens are moved to the right. Then the token column is also not
        deleted.
        """
        line_counter = 0
        column_appended = False

        while line_counter < arr.shape[0]:
            token_type = self._get_type(arr[line_counter, token_col_nr])
            if token_type != self._null_type:
                # onyl non-NULL values are considered

                # move token to the left cell if the type matches and the cell
                # to the left is empty
                if l_col_type != self._invalid and token_type == l_col_type \
                        and arr[line_counter, token_col_nr-1] == self._null:

                    arr[line_counter, token_col_nr-1] = \
                        arr[line_counter, token_col_nr]
                    arr[line_counter, token_col_nr] = self._null

                else:  # move the token to the right...

                    # ...but only if we're not in the rightmost column
                    if r_col_type != self._invalid:

                        # check if right neigbor cell is empty
                        if arr[line_counter, token_col_nr+1] == self._null:
                            # easy case: just move cell value to right
                            # neighbor cell
                            arr[line_counter, token_col_nr+1] = \
                                arr[line_counter, token_col_nr]
                            arr[line_counter, token_col_nr] = self._null

                        else:
                            # append a new column (if not done, yet) and move
                            # all right neighbor cells of the same line one
                            # cell to the right
                            if not column_appended:
                                new_col = np.chararray((self._line_counter, 1),
                                                       self._max_token_str_len)
                                new_col.fill(self._null)
                                arr = np.append(arr, new_col, 1)
                                column_appended = True
                            c = arr.shape[1] - 2

                            while c >= token_col_nr:
                                # copy to the right
                                arr[line_counter, c+1] = arr[line_counter, c]
                                c -= 1
                            arr[line_counter, token_col_nr] = self._null
            line_counter += 1

        # delete the considered column, if it could be emptied completely
        col_types = self._get_types(arr[:, token_col_nr])
        if len(col_types) == 1 and col_types.popitem()[0] == self._null_type:

            arr = np.delete(arr, (token_col_nr), 1)
            token_col_nr -= 1
        else:
            # the token column is marked as mixed column
            self._token_col_types.append(self._mixed)

        return arr

    def _move_from_col(self, arr, token_col_nr,
                       token_col_type, l_col_type, r_col_type):
        """This method moves tokens that are not NULL and do not match the
        token columns predominant type. First it is tried to move tokens to the
        left side. This is done when the token's type matches the token
        column's type and the left neighbor cell is empty. Otherwise cells are
        moved to the right. In case, the right neighbor cell is not empty, the
        whole 'sub line' is moved.
        """
        column_appended = False
        line_counter = 0

        while line_counter < arr.shape[0]:
            token_type = self._get_type(arr[line_counter, token_col_nr])

            if token_type != token_col_type and token_type != self._null:
                # only non-NULL tokens are considered that are not of the
                # column's type

                # move to left if the type of the column to the left matches
                # and the left neighbor cell is empty
                if l_col_type != self._invalid and token_type == l_col_type \
                        and arr[line_counter, token_col_nr-1] == self._null:

                    arr[line_counter, token_col_nr-1] = \
                        arr[line_counter, token_col_nr]
                    arr[line_counter, token_col_nr] = self._null

                else:  # move to right
                    # if the right neighbor cell is not empty, a new column has
                    # to be added before moving (if not done already)
                    if r_col_type != self._invalid and \
                            arr[line_counter, token_col_nr+1] == self._null:
                        # easy case: just move cell value to
                        # right neighbor cell
                        arr[line_counter, token_col_nr+1] = \
                            arr[line_counter, token_col_nr]
                        arr[line_counter, token_col_nr] = self._null
                    else:
                        # append a new column (if not done, yet) and move all
                        # right neighbor cells of the same line one cell to
                        # the right
                        if not column_appended:
                            # TODO: self._line_counter vs arr.shape[0] --> was
                            # not in sync anymore when _move_from_len_col was
                            # called
                            new_col = np.chararray((self._line_counter, 1),
                                                   self._max_token_str_len)
                            new_col.fill(self._null)
                            arr = np.append(arr, new_col, 1)
                            column_appended = True
                        c = arr.shape[1] - 2

                        while c >= token_col_nr:
                            # copy to the right
                            arr[line_counter, c+1] = arr[line_counter, c]
                            c -= 1
                        arr[line_counter, token_col_nr] = self._null
            line_counter += 1

        self._token_col_types.append(token_col_type)

        return arr

    # FIXME: infinite loop in tests
    def _homogenize_on_types(self, arr):
        """This method aims at homogenizing the input array based on the
        datatypes of the actual tokens.
        """
        token_col_nr = 0

        while token_col_nr < arr.shape[1]:
            # check if there is a predominant type
            types = self._get_types(arr[:, token_col_nr])

            # 1) the token column is homogeneous with respect to its type
            #    so nothing has to be done here
            if len(types) == 1:
                self._token_col_types.append(types.popitem()[0])

            else:
                predom_type = None
                predom_type_count = 0
                whole_count = 0
                for type_ in types:
                    type_count = types[type_]
                    whole_count += type_count
                    if type_count > predom_type_count:
                        predom_type = type_
                        predom_type_count = type_count
                self._token_col_types.append(predom_type)
                ratio = predom_type_count/whole_count

                # 2) the token column has a predominant type
                if ratio > self._threshold:

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

                    # Now, it has to be further distinguished between the case
                    # where the predominant token colum type is the NULL type
                    # or something else. In the NULL case, all tokens are moved
                    # to the left or right and the actual token column is then
                    # deleted. In all other cases, tokens that are not of the
                    # predominant type are moved (except NULL tokens, of
                    # course)

                    # i) predominant type is self._null_type --> column is
                    #    sparse
                    if predom_type == self._null_type:
                        # --> move *all* cells to the right or left to empty
                        # the column and delete it afterwards (actually I just
                        # *copy* the values to the left or right and then
                        # delete the column)
                        arr = self._move_from_null_col(arr, token_col_nr,
                                                       left_col_type,
                                                       right_col_type)

                    # ii) predominant type is not self._null_type
                    else:
                        arr = self._move_from_col(arr,
                                                  token_col_nr,
                                                  predom_type,
                                                  left_col_type,
                                                  right_col_type)
                # 3) the token column is mixed
                else:
                    pass

            token_col_nr += 1

        return arr

    def _get_length_count(self, token_col, length):
        count = 0
        for token in token_col:
            if self._get_type(token) == self._str:
                if len(token) == length:
                    count += 1
        return count

    def _move_from_len_col(self, arr, token_col_nr, length):
        """This method homogenizes token columns considering string tokens with
        fixed string lenghths. Accordingly, tokens with a string length that
        differs from the predominant length in column to clean have to be
        moved. Again, first it is tried to move tokens to the lefthand column.
        This only works if the left column is a string column, and in case it
        also has a fixed string length this length mus also match the string
        length of the token to move. Moreover, the left neighbor cell must also
        be empty.
        If moving the token to the left is not possible, it is moved to the
        right. If the right hand column is not of string type or in case the
        right neighbor cell is already assigned, a new column has to be
        introduced.
        *Assumption*: the token columns are already homogenized on their types
        """
        line_counter = 0
        while line_counter < arr.shape[0]:
            token_len = len(arr[line_counter, token_col_nr])

            if token_len != length:
                # try to move it to the left column --> check if the left
                # column is a string column and if it has a fixed str len check
                # whether the str len matches and if the left neighbor cell is
                # empty
                if self._token_col_types[token_col_nr-1] == self._str and \
                        (self._token_col_lengths[token_col_nr-1] == token_len
                         or self._token_col_lengths[token_col_nr-1] == -1) and \
                        arr[line_counter, token_col_nr-1] == self._null:

                    arr[line_counter, token_col_nr-1] = \
                        arr[line_counter, token_col_nr]
                    arr[line_counter, token_col_nr] = self._null

                else:  # move to the right column
                    # The token can only be moved to the right neighbor cell if
                    # - the type of the right neigbor column is self._str
                    # - the cell is empty
                    # - there is a right column
                    if token_col_nr+1 == arr.shape[1]:
                        r_col_type = self._invalid
                    else:
                        r_col_type = self._token_col_types[token_col_nr+1]

                    if r_col_type == self._str and \
                            arr[line_counter, token_col_nr+1] == self._null:

                        arr[line_counter, token_col_nr+1] = \
                            arr[line_counter, token_col_nr]
                        arr[line_counter, token_col_nr] = self._null

                    else:  # a new column has to be introduced
                        new_col = np.chararray((arr.shape[0], 1),
                                               self._max_token_str_len)
                        new_col.fill(self._null)

                        l_arr = arr[:, :token_col_nr+1]
                        r_arr = arr[:, token_col_nr+1:]

                        arr = np.append(l_arr, new_col, 1)
                        arr = np.append(arr, r_arr, 1)

                        self._token_col_types = \
                            self._token_col_types[:token_col_nr] + \
                            [self._str] + \
                            self._token_col_types[token_col_nr:]

                        arr[line_counter, token_col_nr+1] = \
                            arr[line_counter, token_col_nr]
                        arr[line_counter, token_col_nr] = self._null
            line_counter += 1
        return arr

    def _homogenize_on_token_len(self, arr, length):
        """This method aims at homogenizing the input array based on the string
        lengths of sort tokens to align the array based on abbreviation token
        columns
        """
        token_col_nr = 0
        while token_col_nr < arr.shape[1]:
            # check if there is a predominant str len
            length_count = self._get_length_count(arr[:, token_col_nr], length)
            if length_count/arr.shape[0] > self._threshold:
                self._move_from_len_col(arr, token_col_nr, length)
            else:
                self._token_col_lengths.append(-1)
            token_col_nr += 1
        return arr

    def _merge_cols(self, arr):
        """TODO: comment
        """
        token_col_nr = 1
        while token_col_nr < arr.shape[1]:
            type_left_col = self._token_col_types[token_col_nr-1]
            type_curr_col = self._token_col_types[token_col_nr]

            fixed_len_left_col = self._token_col_lengths[token_col_nr-1] > 0
            fixed_len_curr_col = self._token_col_lengths[token_col_nr] > 0

            if token_col_nr == len(self._token_col_types)-1:
                # we're in the rightmost  column
                type_rght_col = self._invalid
                fixed_len_rght_col = False
            else:
                type_rght_col = self._token_col_types[token_col_nr+1]
                fixed_len_rght_col = self._token_col_lengths[token_col_nr+1] > 0

            line_counter = 0
            while line_counter < arr.shape[0]:
                cell = arr[line_counter, token_col_nr]
                if cell == self._null:
                    continue

                is_empty_left = arr[line_counter, token_col_nr-1] == self._null
                if type_rght_col == self._invalid:
                    is_empty_rght = False
                else:
                    is_empty_rght = \
                        arr[line_counter, token_col_nr+1] == self._null

                line_counter += 1

                signature = (
                    type_left_col,
                    fixed_len_left_col,
                    is_empty_left,
                    type_curr_col,
                    fixed_len_curr_col,
                    self._is_sparse(arr[:,token_col_nr]),
                    type_rght_col,
                    fixed_len_rght_col,
                    is_empty_rght
                )

                fn = self._merge_cases.get(signature)
                fn(arr, line_counter, token_col_nr)

                # TODO: IF LINE EMPTY --> REMOVE; token_col_nr -= 1


            # # TODO: merge to the right?
            # type_left = self._token_col_types[token_col_nr-1]
            # type_curr = self._token_col_types[token_col_nr]
            # if type_left == type_curr:

            #     # 3 cases:
            #     # 1) type == string and the column lengths match
            #     #    --> mergeable only if respective neighbor cols are empty
            #     if type_curr == self._str:
            #         len_left = self._token_col_lengths[token_col_nr-1]
            #         len_curr = self._token_col_lengths[token_col_nr]

            #         if len_left == len_curr and len_curr > 0:
            #             # check if 
            #             pass

            #     # 2) type == string and there is no column length restriction
            #     #    --> concat merge (TODO: insert white space!!)
            #         else:
            #             pass
            #     # 3) type != string
            #     #    --> mergeable only if respective neighbor cols are empty
            #     else:
            #         pass
            # else:
            #     # if column is sparse and left col has str type without fixed
            #     # lenghth --> concat merge
            #     # if column is sparse and left col doesn't have type without
            #     # fixed lenghth --> try to concat merge with right col
            #     pass

    def _is_sparse(self, col):
        """Checks if a given column is sparse, i.e. whether the prevalent
        values are NULL values (with respect to the configured threshold)
        """
        num_null_vals = len(np.where(col==self._null)[0])
        num_vals = col.shape[0]
        return (num_null_vals / num_vals ) >= self._threshold

    def get_data(self):
        """returns a homogenized version of the input column
        """
        arr = self._create_array()
        self._token_col_types = []
        arr = self._homogenize_on_types(arr)
        for i in range(4):
            arr = self._homogenize_on_token_len(arr, 2)
        arr = self._merge_cols(arr)

        return arr
