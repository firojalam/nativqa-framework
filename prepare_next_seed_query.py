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
    # data = []
    with open(filepath) as f:
        lines = [line.strip() for line in f.read().strip().split("\n")]
    return lines

def read_completed(filepath):
    # data = []
    queries = open(filepath, 'r', encoding='utf-8').read().strip().split("\n")
    return queries

def write_file(filepath, data):
    f = open(filepath, 'w', encoding='utf-8')
    for query in data:
        f.write(query + "\n")

def get_category(fname):
    parent = ''
    if 'egypt' in fname:
        parent = 'egypt_'
    elif 'khaliji' in fname:
        parent = 'khaliji_'
    elif 'sudan' in fname:
        parent = 'sudan_'
    elif 'tunisia' in fname:
        parent = 'tunisia_'
    elif 'yamani' in fname:
        parent = 'yamani_'
    elif 'jordan' in fname:
        parent = 'jordan_'
    elif 'msa' in fname:
        parent = 'msa_'

    if 'animals' in fname:
        return parent + 'animals'
    elif 'business' in fname:
        return parent + 'business'
    elif 'cloths' in fname:
        return parent + 'cloths'
    elif 'events' in fname:
        return parent + 'events'
    elif 'food_drinks' in fname:
        return parent + 'food_drinks'
    elif 'education' in fname:
        return parent + 'education'
    elif 'general' in fname:
        return parent + 'general'
    elif 'geography' in fname:
        return parent + 'geography'
    elif 'immigration' in fname:
        return parent + 'immigration'
    elif 'language' in fname:
        return parent + 'language'
    elif 'literature' in fname:
        return parent + 'literature'
    elif 'names' in fname:
        return parent + 'names'
    elif 'plants' in fname:
        return parent + 'plants'
    elif 'religion' in fname:
        return parent + 'religion'
    elif 'sports' in fname:
        return parent + 'sports'
    elif 'tradition' in fname:
        return parent + 'tradition'
    elif 'travel' in fname:
        return parent + 'travel'
    elif 'weather' in fname:
        return parent + 'weather'
    else:
        return parent + 'unknown'

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input_dir', action="store", dest="input_dir", default=None, type="string",
                      help='input files directory to scrape')
    parser.add_option('-o', '--output_dir', action='store', dest="output_dir", default=None, type="string",
                      help="Output directory location")
    parser.add_option('-c', '--completed', action='store', dest="completed", default=None, type="string",
                      help="completed query filepath")

    options, args = parser.parse_args()
    input_dir = options.input_dir
    # query_key = options.query_key
    output_dir = options.output_dir
    completed_file = options.completed

    if input_dir is None:
        raise ValueError('input file is required!')
    if output_dir is None:
        output_dir = './data/next_batch/'
    if completed_file is None:
        completed_file = './data/completed/completed_queries.txt'

    ensure_directory(output_dir)
    completed_query = read_completed(completed_file)
    count = 0
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(".txt"):
                data = read_data(file_path)
                category = get_category(file_path)
                if output_dir.endswith('/'):
                    output_file = output_dir + f'{category}.txt'
                else:
                    output_file = output_dir + f'/{category}.txt'
                output_data = []
                for seed in data:
                    if seed.strip() not in completed_query and seed.strip() not in output_data:
                        output_data.append(seed.strip())
                        count += 1
                write_file(output_file, output_data)
    print(f"Total new Queries: {count}")
