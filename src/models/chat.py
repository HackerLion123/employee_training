from src.models.agent import ChatAgent

from PIL import Image

import streamlit as st


def generate_response(input):
    agent = ChatAgent()
    agent.build()

    return agent.chat({"question": input})


if __name__ == "__main__":
    output = generate_response("how to do backfill?")
    print(output)
