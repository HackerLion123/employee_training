from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_chroma import Chroma
from src import config


def generate_embeddings(docs):

    print("Starting to generate embeddings...")

    embeddings = OllamaEmbeddings(**config.EMBEDDING_MODEL_CONFIG)
    print("Embeddings model initialized.")

    # Create Emdeddings
    db = Chroma.from_documents(
        documents=docs, embedding=embeddings, persist_directory=config.EMBEDDING_PATH
    )
    # Load Embeddings
    db = Chroma(embedding_function=embeddings, persist_directory=config.EMBEDDING_PATH)
    print("Database created from documents.")

    # print(db.similarity_search("holidays 2025"))

    # db.persist()
    # print("Database persisted.")

    return db
