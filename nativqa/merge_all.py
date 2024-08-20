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
    with open(filepath, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        for row in data:
            writer.writerow(row)

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
        output_dir = './data/combined/'

    ensure_directory(output_dir)
    header = ['data_id', 'category', 'input_query', 'question', 'answer', 'question_type', 'answer_URLs']
    output = []
    filtered_output = [header]

    duplicate = [header]

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith("all_related_question_answers.tsv"):
                data = read_data(file_path)
                output.extend(data)

    for row in output:
        flag = False
        for data in filtered_output:
            if row[3].strip() == data[3].strip() and row[4].strip() == data[4].strip():
                flag = True
        if not flag:
            filtered_output.append(row)
        else:
            duplicate.append(row)

    if output_dir.endswith('/'):
        output_file = output_dir + 'combined_qa.tsv'
        duplicate_file = output_dir + 'duplicate_qa.tsv'
    else:
        output_file = output_dir + '/combined_qa.tsv'
        duplicate_file = output_dir + '/duplicate_qa.tsv'
    print(f'Total unique data collected: {len(filtered_output)}')
    print(f'Total duplicate data collected: {len(duplicate)}')
    print(f'writing output to: {output_file}')
    write_file(output_file, filtered_output)
    print(f'writing duplicate to: {duplicate_file}')
    write_file(duplicate_file, duplicate)


