import csv
import json
import os
import optparse
from pathlib import Path


def ensure_directory(path):
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
            print(f"Directory '{path}' was created.")
        except OSError as error:
            print(f"Creation of the directory '{path}' failed due to: {error}")
    else:
        print(f"Directory '{path}' already exists.")

def read_data(filepath):
    data = []
    with open(filepath) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)
        for row in reader:
            data.append(row)
    return data

def write_file(filepath, data):
    f = open(filepath, 'w', encoding='utf-8')
    for query in data:
        f.write(query + "\n")

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input_dir', action="store", dest="input_dir", default=None, type="string",
                      help='input files directory to scrape')
    parser.add_option('-o', '--output_dir', action='store', dest="output_dir", default=None, type="string",
                      help="Output directory location")

    options, args = parser.parse_args()
    input_dir = options.input_dir
    # query_key = options.query_key
    output_dir = options.output_dir

    if input_dir is None:
        raise ValueError('input file is required!')
    if output_dir is None:
        output_dir = './data/completed/'

    ensure_directory(output_dir)
    output = []
    filtered_output = []
    # duplicate = []

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith("all_related_question_answers.tsv"):
                data = read_data(file_path)
                output.extend(data)

    for row in output:
        if row[2].strip() not in filtered_output:
            filtered_output.append(row[2].strip())
        # else:
        #     duplicate.append(row)

    if output_dir.endswith('/'):
        output_file = output_dir + 'completed_queries.txt'
    else:
        output_file = output_dir + '/completed_queries.txt'
    print(f'Total completed queries: {len(filtered_output)}')
    print(f'writing output to: {output_file}')
    write_file(output_file, filtered_output)


