import numpy as np


class ColSplitter(object):
    """TODO: implement
    TODO: test
    """

    _int = 'int'
    _float = 'float'
    _str = 'str'
    _fixed_len = 'fixed len'
    _null = b'NULL'
    _null_type = 'null'
    _invalid = 'invalid'
    _valid = 'valid'
    _mixed = 'mixed'

    def __init__(self, delimiter=' ', threshold=0.7):
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
        """Assumption: the token columns are already homogenized on their types
        TODO: comment
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

    def get_data(self):
        """returns a homogenized version of the input column
        """
        arr = self._create_array()
        self._token_col_types = []
        arr = self._homogenize_on_types(arr)
        self._homogenize_on_token_len(arr, 2)

        return arr
