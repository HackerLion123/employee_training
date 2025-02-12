from langchain.document_loaders import DirectoryLoader, PyMuPDFLoader
import os


from docx import Document


def load_word_document(filename):
    doc = Document(filename)
    full_text = []

    for para in doc.paragraphs:
        full_text.append(para.text)

    # Combine all paragraphs into a single string
    document_text = "\n".join(full_text)

    # Convert the text to lowercase
    document_text_lower = document_text.lower()

    return document_text_lower


class DataLoader:
    def __init__(self) -> None:
        pass

    def load_data_from_folder(self, folder_path):
        docs = []
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if filename.endswith(".pdf"):
                loader = PyMuPDFLoader(file_path)
                docs.extend(loader.load())
            elif filename.endswith(".docx"):
                doc = load_word_document(file_path)
                docs.append(doc)
        return docs


if __name__ == "__main__":
    data_object = DataLoader()
    docs = data_object.load_data_from_folder("data/raw/")
