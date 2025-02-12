import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
OPENAI_API_TYPE = os.getenv("AZURE_OPENAI_API_TYPE")
OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_ENDPOINT")
OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYEMENT_NAME = os.getenv("AZURE_OPENAI_API_DEPLOYMENT_NAME")

AZURE_MODEL_CONFIG = {}

MODEL_CONFIG = {
    "base_url": "http://localhost:11434",
    "model": "llama3.2",  # "llama3.1",  # "mistral",  # "mistral-nemo",
    "temperature": 0,
    "keep_alive": 10000,
    "num_gpu": -1,
}

EMBEDDING_MODEL_CONFIG = {"model": "mxbai-embed-large"}


EMBEDDING_PATH = "data/processed/"

DEBUG_FLAG = True

LLM_CACHE_PATH = "data/cache/"
