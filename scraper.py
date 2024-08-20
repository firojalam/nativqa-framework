from serpapi import GoogleSearch
import time
import optparse
import os
import json
import csv
from dotenv import load_dotenv
from pathlib import Path
from tqdm import tqdm


def read_data(filepath):
    query_texts = []
    lines = open(filepath, encoding='utf-8').read().strip().split("\n")
    for line in lines:
        if line.strip() != "":
            query_texts.append(line)
    return query_texts

def read_failed_data(filepath):
    q_texts = []
    with open(filepath, encoding='utf-8') as f:
        lines = f.read().strip().split("\n")
    if len(lines) == 1 and lines[0] == '':
        return q_texts
    else:
        for line in lines:
            dict_obj = json.loads(line)
            q_texts.append(dict_obj['query'])
        return q_texts

def read_summary_data(filepath):
    data = []
    with open(filepath) as f:
        lines = f.read().strip().split("\n")
    # print(lines)
    if len(lines) == 1 and lines[0] == '':
        return data
    else:
        for line in lines:
            data.append(json.loads(line))
        return data

def write_init_summary(filewriter, data):
    for line in data:
        filewriter.write(f"{json.dumps(line, ensure_ascii=False)}\n")
    return filewriter

def write_file(filepath, out_data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(out_data, f, ensure_ascii=False)

def write_csv_file(out_file, rqa_data, delim='\t'):
    with open(out_file,'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=delim)
        for row in rqa_data:
            writer.writerow(row)


def scrape(data, location, gl, summary_writer, failed_writer):
    search_params = {
        "engine": "google",
        "q": "",
        "location": location,
        "gl": gl,
        "safe": "active",
        "api_key": os.getenv('API_KEY')
    }
    # output_response = []

    for query in data:
        search_params['q'] = query.strip()
        try:
            search = GoogleSearch(search_params)
            response = search.get_dict()
            # output_response.append(response)
            summary_writer.write(f"{json.dumps(response, ensure_ascii=False)}\n")
        except Exception as e:
            entry = {"query": query, "Error": str(e)}
            failed_writer.write(f"{json.dumps(entry, ensure_ascii=False)}\n")

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('-i', '--input_dir', action="store", dest="input_dir", default=None, type="string",
                      help='input files directory to scrape')
    parser.add_option('-c', '--country_code', action='store', dest="country_code", default="qa", type="string",
                      help="Country code supported by Google")
    parser.add_option('-l', '--location', action='store', dest="location", default="Doha, Qatar", type="string",
                      help="Country code supported by Google")
    # parser.add_option('-q', '--query_key', action="store", dest="query_key", default=None, type='string',
    #                  help="define the query key to search")
    parser.add_option('-e', '--env', action='store', dest='env', default=None, type="string",
                      help='API key file')

    options, args = parser.parse_args()
    input_dir = options.input_dir
    # query_key = options.query_key
    gl = options.country_code
    location = options.location
    env = options.env
    if input_dir is None:
        raise ValueError('input file is required!')
    #if query_key is None:
    #    raise ValueError('Query key is required!')
    if env is None:
        raise ValueError('API key file is required to use SerpApi!')
    else:
        load_dotenv(env)

    result_dir = input_dir + '/output/'
    if input_dir.endswith('/'):
        result_dir = input_dir + 'output/'

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith(".txt"):
                xPath = Path(file_path)
                parent = str(xPath.parent)
                c_folder = xPath.name.rsplit('.')  # [0] + '.json'
                c_folder = ".".join(c_folder[:-1])  # + '_failed.jsonl'
                if "output/" in file_path:
                    continue
                folder_name = os.path.splitext(os.path.basename(file_path))[0]
                working_dir = result_dir + folder_name  # parent + c_folder
                if not os.path.isdir(working_dir):
                    os.makedirs(working_dir, exist_ok=True)
                #response_dir = working_dir + '/original_response/'
                #question_dir = working_dir + '/related_questions/'
                summary = working_dir + f'/{folder_name}_summary.jsonl'
                failed = working_dir + f'/{folder_name}_failed.jsonl'
                #if not os.path.isdir(response_dir):
                #    os.makedirs(response_dir, exist_ok=True)

                #if not os.path.isdir(question_dir):
                #    os.makedirs(question_dir, exist_ok=True)

                if not os.path.exists(failed):
                    check_cache = False
                else:
                    check_cache = True
                failed_data = []
                if check_cache:
                    failed_data = read_failed_data(failed)

                # get summary
                summary_data = []
                if os.path.exists(summary):
                    summary_data = read_summary_data(summary)
                summary_writer = open(summary, 'w', encoding='utf-8')
                if len(summary_data) > 0:
                    print('writing initial summary')
                    summary_writer = write_init_summary(summary_writer, summary_data)

                failed_writer = open(failed, 'w', encoding='utf-8')
                # read data
                print(f'reading file: {file_path}...')
                data = read_data(file_path)

                if len(failed_data) > 0:
                    if len(failed_data) + len(summary_data) != len(data):
                        # print("scrapping both failed and rest data")
                        print(f'Skipping total data: {len(summary_data)}')
                        # print("failed, continuing from failed first followed by summary")
                        # first try to scrape failed data, then try to scrape rest
                        scrape(failed_data, location, gl, summary_writer, failed_writer)
                        start_index = len(failed_data)+len(summary_data)
                        data = data[start_index:]
                        scrape(data, location, gl, summary_writer, failed_writer)
                    else:
                        # scrape only failed data
                        # print("scrapping only failed data")
                        scrape(failed_data, location, gl, summary_writer, failed_writer)
                else:
                    # no failed data, need to check summary data
                    if len(summary_data) == len(data):
                        print('All the data is translated!')
                    elif len(summary_data) > 0:
                        # print("No failed, only continuing from summary")
                        print(f'Skipping total data: {len(summary_data)}')
                        data = data[len(summary_data):]
                        scrape(data, location, gl, summary_writer, failed_writer)
                    else:
                        # starting from input file
                        # print("starting from input file")
                        scrape(data, location, gl, summary_writer, failed_writer)
                summary_writer.close()
                failed_writer.close()
                # Generating final output files
                # 1. original response
                # 2. related questions
                # 3. question answers
                # 4. a generalized tsv file containing query text, question, answers, category, and url
                output_data = read_summary_data(summary)
                out_file = working_dir + f'/{folder_name}_original_response.json'
                print(f'writing response to: {out_file}...')
                write_file(out_file, output_data)

                header = ['Input Query', 'Question', 'Answer', 'Question Type', 'Answer URLS']
                rqa_resp = [header]
                rquestion_resp = []
                qa_response = []

                for results in output_data:
                    null_entry = True
                    if 'related_questions' in results:
                        null_entry = False
                        for entry in results['related_questions']:
                            # print(entry)
                            ans = ''
                            if 'snippet' in entry:
                                ans = entry['snippet']
                            elif 'list' in entry:
                                ans = "\n".join(entry['list'])
                            rqa_resp.append([results['search_parameters']["q"], entry['question'], ans, 'related_questions', entry['link']])
                        rq = {'search_parameters': results['search_parameters'], 'related_questions': results['related_questions']}
                        rquestion_resp.append(rq)
                    if 'questions_and_answers' in results:
                        null_entry = False
                        for entry in results['related_questions']:
                            # print(entry)
                            rqa_resp.append(
                                [results['search_parameters']["q"], entry['question'], entry['answer'], 'questions_and_answers', entry['link']])
                        rq = {'search_parameters': results['search_parameters'],
                              'questions_and_answers': results['questions_and_answers']}
                        qa_response.append(rq)
                    if null_entry:
                        rqa_resp.append([results['search_parameters']["q"], 'Not Available', 'NA', 'NA', 'NA'])

                out_file = working_dir + f'/{folder_name}_related_questions.json'
                print(f'writing response to: {out_file}...')
                write_file(out_file, rquestion_resp)
                out_file = working_dir + '/questions_answers.json'
                print(f'writing response to: {out_file}...')
                write_file(out_file, qa_response)

                out_file = working_dir + f'/{folder_name}_all_related_question_answers.tsv'
                print(f'writing response to: {out_file}...')
                write_csv_file(out_file, rqa_resp, delim='\t')
                unique_qa = [rqa_resp[0]]
                temp = []
                for row in rqa_resp[1:]:
                    if row[1].strip() not in temp and row[1] !='NA':
                        temp.append(row[1].strip())
                        unique_qa.append(row)
                out_file = working_dir + f'/{folder_name}_unique_questions.tsv'
                print(f'writing response to: {out_file}...')
                write_csv_file(out_file, unique_qa, delim='\t')


