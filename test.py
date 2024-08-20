from serpapi import GoogleSearch
import csv
import json

api_key = "4801d29b916afd20f5fd5b636ee3a88b2df5568c302bd3882bc343c49d73e1ec"
name = 'education'
filename = f'./test_data/phrase_list_{name}.txt'

with open(filename, encoding='utf-8') as f:
    lines = f.read().strip().split("\n")


params = {
  "engine": "google",
  "q": "",
  "location": "Doha, Doha, Qatar",
  #"hl": "bn",
  "gl": "qa",
  "google_domain": "google.com",
  "num": "20",
  # "start": "10",
  "safe": "active",
  "api_key": api_key
}

header = ['Input Query', 'Question', 'Answer', 'Question Type']

response = []
rquestion_resp = [header]

for query in lines:
    params['q'] = query.strip()
    search = GoogleSearch(params)
    results = search.get_dict()
    response.append(results)
    null_entry = True
    if 'related_questions' in results:
        null_entry = False
        for entry in results['related_questions']:
            #print(entry)
            ans = ''
            if 'snippet' in entry:
                ans = entry['snippet']
            elif 'list' in entry:
                ans = "\n".join(entry['list'])
            rquestion_resp.append([params['q'], entry['question'], ans, 'related_questions'])
    if 'questions_and_answers' in results:
        null_entry = False
        for entry in results['related_questions']:
            #print(entry)
            rquestion_resp.append([params['q'], entry['question'], entry['answer'], 'questions_and_answers'])
    if null_entry:
        rquestion_resp.append([params['q'], 'Not Available', 'NA', 'NA'])

with open(f'./test_data/phrase_list_{name}.doha.tsv', 'w', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter='\t')
    for row in rquestion_resp:
        writer.writerow(row)

with open(f'./test_data/response_phrase_list_{name}.doha.json', 'w') as f:
    json.dump(response, f, ensure_ascii=False)

