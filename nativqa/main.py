from nativqa.extended_query_scrapper import run_extended_query_scrapper
from nativqa.extract_completed_query import run_extract_completed_query
from nativqa.prepare_next_qa_queries import run_prepare_next_qa_queries
from nativqa.prepare_next_rs_query import run_prepare_next_rs_query

def run_workflow():
    # Step 1: Seed
    run_extended_query_scrapper()
    run_extract_completed_query()

    # Step 2: Seed Result - RQA
    run_prepare_next_qa_queries()
    run_extended_query_scrapper()
    run_extract_completed_query()

    # Step 3: Seed Result - RS
    run_prepare_next_rs_query()
    run_extended_query_scrapper()
    run_extract_completed_query()

    # Step 4: 2nd Batch Result - RQA
    run_prepare_next_qa_queries()
    run_extended_query_scrapper()
    run_extract_completed_query()

    # Step 5: 2nd Batch Result - RS
    run_prepare_next_rs_query()
    run_extended_query_scrapper()
    run_extract_completed_query()

    # Step 6: 3rd Batch Result - RQA
    run_prepare_next_qa_queries()
    run_extended_query_scrapper()
    run_extract_completed_query()

if __name__ == "__main__":
    run_workflow()

