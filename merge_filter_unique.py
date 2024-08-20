import csv
import os


def read_data(filepath, delim='\t'):
    data = []
    with open(filepath, encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delim)
        next(reader)
        for row in reader:
            data.append(row)
    return data


def extract_uniques(unique, data):
    pass


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input_dir', action="store", dest="input_dir", default=None, type="string",
                      help='input previous file to merge')
    # parser.add_option('-n', '--new_file', action="store", dest="new_file", default=None, type="string",
    #                   help='input new file to merge')
    options, args = parser.parse_args()
    input_dir = options.input_dir
    # new_file = options.new_file

    unique_questions = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(".txt"):
                continue
