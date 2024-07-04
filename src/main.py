from pipelines.master import run_master_pipeline
from import_from_db import import_all_from_db
import streamlit as st

st.title('Coursedog magic!')

def generate_response(message):
    st.info(run_master_pipeline(message, 5))

with st.form('my_form'):
    text = st.text_area('Enter text:')
    submitted = st.form_submit_button('Submit')
    if submitted:
        generate_response(text)
