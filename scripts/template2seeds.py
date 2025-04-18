import optparse
import csv


def create_seeds(template_fpath, output_file, location):
    data = []
    with open(template_fpath) as f:
        reader = csv.reader(f)
        header = next(reader)
        data.append(header)
        for row in reader:
            row[1] = row[1].replace("[LOCATION]", location)
            data.append(row)

    write_seed_file(data, output_file)


def write_seed_file(data, output_path):
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-i', '--template_file', action="store", dest="template_file", default=None, type="string",
                      help='input template file path')
    parser.add_option('-o', '--output_file', action="store", dest="output_file", default=None, type="string",
                      help="output file path")
    parser.add_option('-l', '--location', action="store", dest="location", default=None, type="string",
                      help="Location to replace in template")

    options, args = parser.parse_args()
    input_file = options.template_file
    output_file = options.output_file
    location = options.location

    create_seeds(input_file, output_file, location)

