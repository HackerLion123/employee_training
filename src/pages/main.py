import streamlit as st

from PIL import Image

import requests
from io import BytesIO

import json


from src.models.chat import generate_response


def generate_page():
    """_summary_"""

    st.set_page_config(page_title="Kmart", page_icon=":books:")
    st.title("Chat with Kmart Assistant")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.chat_message("Assistant"):
        st.markdown("Hello, How can I help you today?")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = generate_response(input=prompt)

        with st.chat_message("assistant"):
            st.markdown(response["generation"])

        st.session_state.messages.append(
            {"role": "assistant", "content": response["generation"]}
        )


def parse_output(output):
    pass
