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

    def __init__(self, delimiter=' ', threshold=0.7):
        self._delimiter = delimiter
        self._threshold = threshold
        self._max_token_str_len = 0
        self._max_line_tokens = 0
        self._token_col_types = []

        # to keep track of the actual line number to write in the numpy array
        self._line_counter = 0

        # list of lists (i.e. pseudo 2d array) containing the actual line tokens
        self._line_tokens = [[]]

    def add_line(self, line):
        """Takes an input line and splits it up to single tokens which are then
        added to self._line_tokens
        """
        tokens = line.split(self._delimiter)
        # FIXME: do I need a dedicated variable here?
        num_tokens = len(tokens)
        self._max_line_tokens = max(self._max_line_tokens, num_tokens)

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

            if types.get(type) == None:
                types[type] = 1
            else:
                type_count = types[type]
                type_count += 1
                types[type] = type_count

        return types

    def _homogenize_on_types(self, arr):
        """This method aims at homogenizing the input array based on the
        datatypes of the actual tokens.
        """
        token_col_nr = 0
        

        while token_col_nr < self._max_line_tokens:
            # check if there is a predominant type
            types = self._get_types(arr[:,token_col_nr])

            # 1) the token column is homogeneous with respect to its type
            #    so nothing has to be done here
            if len(types)==1:
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
                    pass

                else:
                # 3) the token column is mixed
                    pass
            
            token_col_nr += 1

    def get_data(self):
        """returns a homogenized version of the input column
        """
        arr = self._create_array()
        self._homogenize_on_types(arr)


