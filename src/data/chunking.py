from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)

from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

from src import config


def semantic_chunker(docs):
    docs = [
        Document(page_content=doc) if isinstance(doc, Document) == False else doc
        for doc in docs
    ]
    embeddings = OllamaEmbeddings(**config.EMBEDDING_MODEL_CONFIG)
    text_splitter = SemanticChunker(embeddings=embeddings, min_chunk_size=300)

    # Split documents into smaller chunks using text splitter
    chunks = text_splitter.split_documents(docs)
    print(f"Split {len(docs)} documents into {len(chunks)} chunks.")

    # Print example of page content and metadata for a chunk
    document = chunks[0]
    print(document.page_content)
    return chunks
