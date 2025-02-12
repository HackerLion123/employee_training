from src.data.embeddings import generate_embeddings

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from src.data.chunking import semantic_chunker
from src.data.data_loader import DataLoader

from src import config
import os


def create_document_embbedding():
    """_summary_

    Returns:
        _type_: _description_
    """
    data_loader = DataLoader()
    docs = data_loader.load_data_from_folder("data/raw/")
    docs = semantic_chunker(docs)
    print(len(docs))
    generate_embeddings(docs=docs)


def create_retriver():
    embeddings = OllamaEmbeddings(**config.EMBEDDING_MODEL_CONFIG)
    print("Embeddings model initialized.")
    if not os.path.exists(config.EMBEDDING_PATH):
        print("Embeddings not found. Creating new embeddings...")
        create_document_embbedding()

    # Load Embeddings
    db = Chroma(embedding_function=embeddings, persist_directory=config.EMBEDDING_PATH)
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2},
    )
    return retriever


if __name__ == "__main__":
    create_document_embbedding()
    retriver = create_retriver()
    retriver.get_relevant_documents("holiday 2025")
