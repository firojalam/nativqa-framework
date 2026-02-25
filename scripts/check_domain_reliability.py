import csv
import sys
import optparse
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(module)s %(filename)s:%(lineno)s - %(message)s',
                    encoding='utf-8', level=logging.DEBUG)


def get_annotated_domains():
    url2rel = {}
    with open('domain/annotated_domains.csv') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader)
        for row in reader:
            url2rel[row[1]] = row[-1]
    return url2rel


def verify_domains(domains, input_file, output_file):
    unverified_domain = {}

    if input_file.endswith(".csv"):
        in_delim = ','
    elif input_file.endswith(".tsv"):
        in_delim = '\t'
    else:
        logger.error("We support only csv/tsv file for now!")
        sys.exit(1)
    if output_file.endswith(".csv"):
        out_delim = ','
    elif output_file.endswith(".tsv"):
        out_delim = '\t'
    else:
        logger.error("We support only csv/tsv file for now!")
        sys.exit(1)

    unverified = []
    rel_ext = ['.gov', '.edu', '.ac']
    try:
        total = 0
        with open(output_file, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=out_delim)
            with open(input_file, 'r') as fp:
                reader = csv.reader(fp, delimiter=in_delim)
                header = next(reader)
                header.append('is_reliable')
                writer.writerow(header)
                count = 0
                for row in reader:
                    total += 1
                    if row[4].strip() != '':
                        domain = urlparse(row[-1]).netloc
                        if rel_ext[0] in domain or rel_ext[1] in domain or rel_ext[2] in domain:
                            row.append('very_reliable')
                            writer.writerow(row)
                            count += 1
                        elif domain in url2rel:
                            if url2rel[domain] in ['very_reliable']:
                                row.append(url2rel[domain])
                                writer.writerow(row)
                                count += 1
                        elif 'https://' + domain in url2rel:
                            domain = 'https://' + domain
                            if url2rel[domain] in ['very_reliable']:
                                row.append(url2rel[domain])
                                writer.writerow(row)
                                count += 1
                        else:
                            unverified.append(row)
                            if domain not in unverified_domain:
                                unverified_domain[domain] = 0
                            unverified_domain[domain] += 1
    except Exception as e:
        logger.error(e)


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input_file', action="store", dest="input_file", default=None, type="string",
                      help='input file path')
    parser.add_option('-o', '--output_file', action="store", dest="output_file", default=None, type="string",
                      help="output file path")

    options, args = parser.parse_args()
    input_file = options.input_file
    output_file = options.output_file

    if input_file is None or input_file.strip() == "":
        logger.error('Input file is required!')
        sys.exit(1)
    if output_file is None or output_file.strip() == "":
        logger.error('Output file is required!')
        sys.exit(1)

    domains = get_annotated_domains()
    verify_domains(domains, input_file, output_file)

