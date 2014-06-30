import csv
import sys

from colsplit.colsplitter import ColSplitter


def run(input_file_path, outfile_path=None, csv_file_header=False,
        delimiter=',', encoding='utf8', considered_fixed_lengths=[2, 3],
        greedy_merge=True):

    col_names = None
    col_splitters = []

    with open(input_file_path, encoding=encoding) as in_file:
        csv_reader = csv.reader(in_file, delimiter=delimiter)

        first_line = next(csv_reader)

        if csv_file_header:
            # TODO: do I need the col names?
            col_names = first_line

        num_cols = len(first_line)

        for i in range(num_cols):
            col_splitters.append(ColSplitter(
                considered_fixed_lengths=considered_fixed_lengths,
                encoding=encoding, greedy_merge=greedy_merge))
            # col_splitters.append(ColSplitter())
            if not csv_file_header:
                col_splitters[i].add_line(first_line[i])

        num_cols = None
        num_lines = 0 if csv_file_header else 1
        for line in csv_reader:
            if len(line) > 0 and num_cols is None:
                num_cols = len(line)
            for i in range(len(line)):
                col_splitters[i].add_line(line[i])
            num_lines += 1

    if outfile_path is None:
        out_file = sys.stdout
    else:
        out_file = open(outfile_path, 'w')
    csv_writer = csv.writer(out_file)

    results = []
    for splitter in col_splitters:
        results.append(splitter.get_data())

    for line_nr in range(num_lines):
        line = []
        for cs_nr in range(len(col_splitters)):
            result = results[cs_nr]
            try:
                res = result[line_nr, :]
            except IndexError:
                continue

            for field in res:
                if field == col_splitters[cs_nr]._null:
                    line.append('')
                else:
                    line.append(field.decode(encoding))
        csv_writer.writerow(line)

    out_file.close()
