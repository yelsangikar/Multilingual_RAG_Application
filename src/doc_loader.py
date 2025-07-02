from langchain_community.document_loaders import UnstructuredPDFLoader, UnstructuredImageLoader
from langchain.schema import Document
from typing import List
import os


def load_documents_from_folder(folder_path: str) -> List[Document]:
    docs = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        if filename.lower().endswith(".pdf"):
            loader = UnstructuredPDFLoader(file_path)
        elif filename.lower().endswith((".png", ".jpg", ".jpeg")):
            loader = UnstructuredImageLoader(file_path)
        else:
            print(f"Skipping unsupported file: {filename}")
            continue

        docs.extend(loader.load())

    return docs


# 🧪 TEST
if __name__ == "__main__":
    folder = "../docs"  # 📁 Place your Japanese, Chinese, English PDFs/images here
    loaded_docs = load_documents_from_folder(folder)

    for i, doc in enumerate(loaded_docs[:5]):
        print(f"\n--- Document {i + 1} ---\n")
        print(doc.page_content[:1000])  # show first 1000 chars only
