import streamlit as st

def chat():
    msg = st.chat_input("Ask analytics question")
    if msg:
        st.write("LLM reasoning...")
