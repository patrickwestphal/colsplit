import numpy as np
import scipy


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

    def __init__(self, delimiter=' ', threshold=0.7):
        self._delimiter = delimiter
        self._threshold = threshold
        self._max_token_str_len = 0
        self._max_line_tokens = 0
        self._token_col_types = []

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
            type = self._null_type
        else:
            type = self._str

            try:
                float(token)
                type = self._float
            except ValueError:
                pass

            try:
                int(token)
                type = self._int
            except ValueError:
                pass

        return type

    def _get_types(self, token_col):
        types = {}
        for token in token_col:

            type = self._get_type(token)

            if types.get(type) is None:
                types[type] = 1
            else:
                type_count = types[type]
                type_count += 1
                types[type] = type_count

        return types

    def _move_from_null_col(self, arr, token_col_nr, l_col_type, r_col_type):
        """This method moves all tokens of a sparse token column to the
        neighbor columns. First it is tried to move tokens to the left neighbor
        column. This only works if the type of the token matches the type of
        the left neighbor column and the corresponding token cell is empty. In
        all other cases tokens are moved to the right. In case the right
        neighbor cell is not empty, the whole right 'sub line' has to be moved
        after introducing a new column on the rightmost position.
        """
        arr = self._move_from_col(arr, token_col_nr,
                                  self._null_type, l_col_type, r_col_type)

        types = self._get_types(arr[:, token_col_nr])
        if (token_col_nr+1) != arr.shape[1] or \
                (len(types) == 1 and
                 types.types.popitem()[0] == self._null_type):

            arr = np.delete(arr, (token_col_nr), 1)
            token_col_nr -= 1

        return arr

    def _move_from_col(self, arr, token_col_nr,
                       token_col_type, l_col_type, r_col_type):
        column_appended = False
        line_counter = 0

        while line_counter < arr.shape[0]:
            token_type = self._get_type(arr[line_counter, token_col_nr])
            if token_type == token_col_type:
                # token is in the right place; nothing to do here
                pass
            # move to left if the type of the column to the left matches and
            # the left neighbor cell is empty
            elif l_col_type != self._invalid and token_type == l_col_type \
                    and arr[line_counter, token_col_nr-1] == self._null:

                arr[line_counter, token_col_nr-1] = \
                    arr[line_counter, token_col_nr]

            else:
                # move to right or do not move the cell at all
                # -> check if we're in the right most column
                if r_col_type == self._invalid:
                    # do nothing since we're at the last column
                    pass
                else:
                    # check if right neigbor cell is empty
                    r_neighbor = arr[line_counter, token_col_nr+1]
                    if r_neighbor == self._null:
                        # easy case: just move cell value to
                        # right neighbor cell
                        arr[line_counter, token_col_nr+1] = \
                            arr[line_counter, token_col_nr]
                    else:
                        # append a new column (if not done, yet) and move all
                        # right neighbor cells of the same line one cell to
                        # the right
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
            line_counter += 1

        return arr

    def _homogenize_on_types(self, arr):
        """This method aims at homogenizing the input array based on the
        datatypes of the actual tokens.
        """
        token_col_nr = 0

        while token_col_nr < self._max_line_tokens:
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
                for type in self._token_col_types:
                    type_count = self._token_col_types[type]
                    whole_count += type_count
                    if type_count > predom_type_count:
                        predom_type = type
                        predom_type_count = type_count
                ratio = predom_type_count/whole_count

                # 2) the token column has a predominant type
                if ratio > self._threshold:

                    # check if there are values in the column to the right
                    # yes --> valid; no --> invalid (i.e. we're in the last
                    # token column)
                    arr_col_num = char_arr.shape[1]
                    if col_nr == (arr_col_num-1):
                        right_col_type = self._invalid
                    else:
                        right_col_type = self._valid

                    # get type of col to the left (invalid means, there is no
                    # column to the left)
                    if col_nr > 0:
                        left_col_type = col_types[col_nr-1]
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
                        pass
                # 3) the token column is mixed
                else:
                    pass

            token_col_nr += 1

    def get_data(self):
        """returns a homogenized version of the input column
        """
        arr = self._create_array()
        self._homogenize_on_types(arr)
