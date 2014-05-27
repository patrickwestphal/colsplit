import csv
import sys

from colsplit.colsplitter import ColSplitter

def run(input_file_path, outfile_path=None, csv_file_header=False):

    col_names = None
    col_splitters = []

    with open(input_file_path) as in_file:
        csv_reader = csv.reader(in_file)

        first_line = next(csv_reader)

        if csv_file_header:
            # TODO: do I need the col names?
            col_names = first_line
        else:
            col_splitters.append(ColSplitter())

        num_cols = len(first_line)

        for i in range(num_cols):
            col_splitters.append(ColSplitter())

        num_cols = None
        for line in csv_reader:
            if len(line)>0 and num_cols==None:
                num_cols = len(line)
            for i in range(len(line)):

                col_splitters[i].add_line(line[i])

    for splitter in col_splitters:
        splitter.get_data()
    if outfile_path is None:
        out_file = sys.stdout
    else:
        out_file = open(outfile_path, 'w')
    # TODO: write back results
