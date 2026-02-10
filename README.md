# NativQA Framework: Multilingual, Culturally-Aligned Natural Query Collection

[![Project](https://badgen.net/badge/GitLab/nativqa%2Fnativqa-framework/blue)](https://gitlab.com/nativqa/nativqa-framework)
[![Pipeline status](https://gitlab.com/nativqa/nativqa-framework/badges/main/pipeline.svg)](https://gitlab.com/nativqa/nativqa-framework/-/pipelines)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
![Languages](https://img.shields.io/badge/languages-7%2B-brightgreen)

**NativQA Framework** is an open-source Python framework for collecting multilingual, location-specific natural queries and QA pairs from search engines (e.g., "People also ask") using seed queries. It is designed for building culturally aligned QA datasets and for evaluating and fine-tuning large language models (LLMs).

Quick links: [Quick Start](#quick-start) · [Outputs](#outputs) · [Demo](#demo) · [QA Validation](#qa-validation) · [Contributing Guide](./CONTRIBUTING.md) · [Changelog](./CHANGELOG.md) · [Citation](#citation)

## Key Features
<p align="center">
<picture>
<img alt = "NativQA framework, demonstrating the data collection and annotation process." src="nativqa_framework.png" width="510"/>
</picture>
</p>

Developing the **NativQA Framework** is an ongoing effort, and the framework will continue to grow and improve over time. Currently, it offers the following features:

- Supports [Google](https://google.com), [Yahoo](https://yahoo.com), and [Bing](https://www.bing.com) for collecting "People also ask" questions and answers.
- Accepts seed queries in CSV/TSV format.
- Open-source and community-driven.
- Supports image collection for visual question answering tasks.
- Multilingual support for diverse language coverage.

Here is a quick overview of NativQA Framework:
> Video: https://youtu.be/Wd2Gmlcoghk

## Table of Contents

- [Quick Start](#quick-start)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Query Collection](#query-collection)
- [QA Validation](#qa-validation)
- [Demo](#demo)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Contributing Guide (file)](./CONTRIBUTING.md)
- [Changelog (file)](./CHANGELOG.md)
- [License](#license)
- [Citation](#citation)

## Quick Start

1. Clone the repository: `git clone https://gitlab.com/nativqa/nativqa-framework.git`
2. Navigate to the repo: `cd nativqa-framework`
3. Install dependencies: `pip install -r requirements.txt`
4. (Recommended) Install the package locally: `pip install -e .`
5. Put your SerpAPI API key in `envs/api_key.env`
6. Run the program!

For example, to run the program using example seed queries:
```bash
python3 -m nativqa --engine google --search_type text --input_file data/test_query.csv --country_code qa --location "Doha, Qatar" --env envs/api_key.env --n_iter 3
```
which uses a sample [seed query file](./data/test_query.csv)

## Inputs

- Seed query file: CSV/TSV (one query per row).
- API keys: store secrets in `envs/` (for example `envs/api_key.env`).

#### Parameters

- `--engine` Search engine to use for QA collection. Currently supports Google, Bing, and Yahoo.
- `--search_type` Type of search: `text` or `image` (image search currently supports Google only).
- `--input_file` Seed query file (CSV/TSV).
- `--country_code` Country code to use for the search engine.
- `--location` Where you want the search to originate.
- `--multiple_countries` Parameter defines one or multiple countries to limit the search to. For example, `countryQA|countryBD`
- `--env` API key file.
- `--output` Output directory location (default: `./results/`).
- `--n_iter` Number of search iterations to perform.

## Outputs

The framework creates a directory using the input `filename` under the given output directory:

- `dataset/` final QA pairs (derived from the input file).
- `iteration_{n}/` per-iteration artifacts:
  - `output/` includes `related_search.tsv`, `original_response.json`, `summary.jsonl`, `related_question.json`
- `completed_queries.txt` list of completed searched queries

## Query collection

### Template based Query Generation

```
python scripts/template2seeds.py --template_file templates/arabic_template.csv --output_file templates/test.csv --location "قطر"
```

### LLM based Query Generation

Planned.

## QA Validation

### Domain Reliability Check (DRC)

Manually verified domains list file is located in `domain/annotated_domains.csv`.

To verify the answer source reliability: (the input file will be dataset file generated from `nativqa` framework.)

```python
python scripts/check_domain_reliability.py --input_file <dataset_directory>/input_filename.csv --output_file <output_directory>/output_filename.csv
```
Note: only CSV/TSV are currently supported for the domain reliability task.

### LLM based Annotation

```python
python scripts/GPT_4o_labeling.py --input_file results/text/arabic_qa/dataset.json --env_path envs/gpt4-api-key.env --output_dir results/text/arabic_qa/GPT4o_labeling/ --location "Qatar"
```

## Demo

For a lightweight, static "paste seed queries → run → preview JSONL → download" page, see `demo/README.md`.

## Roadmap

- LLM-based query generation workflow
- More output formats and validators
- Expanded image/VQA collection

## Contributing

- Contribution process and guidelines: [`CONTRIBUTING.md`](./CONTRIBUTING.md)
- Release history and upcoming changes: [`CHANGELOG.md`](./CHANGELOG.md)
- Issues and feature requests: use GitLab issues on https://gitlab.com/nativqa/nativqa-framework
- PRs/MRs: small, focused changes with a short description and example command/output
- If you use NativQA in a paper/project, please cite it and consider starring the repo

## License
The **NativQA Framework** is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You are free to share and adapt the framework for **non-commercial purposes**, provided that:

- You give **appropriate credit**.
- You indicate if **changes were made**.
- You distribute your contributions under the **same license**.

## Citation
Please cite our papers when referring to this framework:

```
@article{Alam2024nativqa,
  title={NativQA Framework: A Framework for Collecting Multilingual Culturally-Aligned Natural Queries},
  author={Alam, Firoj and Hasan, Md Arid and Laskar, Sahinur Rahman and Kutlu, Mucahid and Chowdhury, Shammur Absar},
  journal={arXiv},
  year={2024}
}
```
