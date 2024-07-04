from pipelines.master import run_master_pipeline
from import_from_db import import_all_from_db

query = 'What is a good course for someone interested in biology and biomedical engineering?'

run_master_pipeline(query)
