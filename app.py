import streamlit as st
from pipeline_01 import pipeline

st.title('Processador de arquivos')

if st.button('Processador'):
    with st.spinner('Processando...'):
        logs = pipeline()
        # exibe os logs no streamlit
        for log in logs:
            st.write(log)