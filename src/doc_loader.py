# src/doc_loader.py

import os
import base64
import pickle
from PIL import Image
from io import BytesIO
import fitz  # PyMuPDF
from typing import List
from tempfile import NamedTemporaryFile

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o", max_tokens=1000)

CACHE_FILE = "processed_docs.pkl"
#
def extract_text_from_image_with_gpt(image_path):
    with open(image_path, "rb") as img_file:
        b64 = base64.b64encode(img_file.read()).decode()

    message = HumanMessage(content=[
        {"type": "text", "text": "Extract text and describe the image. Languages: Japanese, English, Chinese."},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
    ])

    response = llm.invoke([message])
    return response.content

def extract_images_from_pdf(pdf_path):
    images = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            image_name = f"{os.path.basename(pdf_path)}_page{i+1}_img{img_index+1}.{ext}"
            image_path = f"temp_{image_name}"
            image.save(image_path)
            images.append((image_path, image_name))
    return images

def load_documents(folder_path):
    if os.path.exists(CACHE_FILE):
        print("🧠 Cached documents found. Loading from disk...")
        with open(CACHE_FILE, "rb") as f:
            return pickle.load(f)

    print("📥 No cache found. Loading and processing documents...")
    docs = []

    for file in os.listdir(folder_path):
        path = os.path.join(folder_path, file)

        if file.lower().endswith(".pdf"):
            print(f"📄 Loading PDF: {file}")
            loader = PyMuPDFLoader(path)
            docs.extend(loader.load())

            print(f"🖼️ Extracting images from PDF: {file}")
            images = extract_images_from_pdf(path)
            for img_path, img_name in images:
                extracted = extract_text_from_image_with_gpt(img_path)
                docs.append(Document(page_content=extracted, metadata={"source": img_name}))
                os.remove(img_path)

        elif file.lower().endswith((".png", ".jpg", ".jpeg")):
            print(f"🖼️ Loading image: {file}")
            extracted = extract_text_from_image_with_gpt(path)
            docs.append(Document(page_content=extracted, metadata={"source": file}))

    # ✅ Save to cache
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(docs, f)

    print("✅ Documents processed and cached.")
    return docs

def load_document_from_upload(filename: str, file_bytes: bytes) -> List[Document]:
    ext = filename.lower().split('.')[-1]
    docs = []

    # Save temp file
    with NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if ext == "pdf":
            print(f"📄 Processing uploaded PDF: {filename}")
            loader = PyMuPDFLoader(tmp_path)
            docs.extend(loader.load())

            print("🖼️ Extracting images from PDF...")
            images = extract_images_from_pdf(tmp_path)
            for img_path, img_name in images:
                extracted = extract_text_from_image_with_gpt(img_path)
                docs.append(Document(page_content=extracted, metadata={"source": img_name}))
                os.remove(img_path)

        elif ext in ["png", "jpg", "jpeg"]:
            print(f"🖼️ Processing uploaded image: {filename}")
            extracted = extract_text_from_image_with_gpt(tmp_path)
            docs.append(Document(page_content=extracted, metadata={"source": filename}))

        elif ext == "txt":
            print(f"📄 Processing uploaded text file: {filename}")
            content = file_bytes.decode("utf-8")
            docs.append(Document(page_content=content, metadata={"source": filename}))

        else:
            print(f"⚠️ Unsupported file type: {ext}")

    finally:
        os.remove(tmp_path)

    return docs




# # src/doc_loader.py
#
# import os
# import base64
# from PIL import Image
# from io import BytesIO
# import fitz  # PyMuPDF
#
# from langchain_community.document_loaders import PyMuPDFLoader
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage
# from langchain_core.documents import Document
# from dotenv import load_dotenv
#
# load_dotenv()  # Load API key from .env
#
# llm = ChatOpenAI(model="gpt-4o", max_tokens=1000)
#
# def extract_text_from_image_with_gpt(image_path):
#     with open(image_path, "rb") as img_file:
#         b64 = base64.b64encode(img_file.read()).decode()
#
#     message = HumanMessage(content=[
#         {"type": "text", "text": "Extract text and describe the image. Languages: Japanese, English, Chinese."},
#         {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
#     ])
#
#     response = llm.invoke([message])
#     return response.content
#
# def extract_images_from_pdf(pdf_path):
#     images = []
#     doc = fitz.open(pdf_path)
#     for i, page in enumerate(doc):
#         for img_index, img in enumerate(page.get_images(full=True)):
#             xref = img[0]
#             base_image = doc.extract_image(xref)
#             image_bytes = base_image["image"]
#             ext = base_image["ext"]
#             image = Image.open(BytesIO(image_bytes)).convert("RGB")
#             image_name = f"{os.path.basename(pdf_path)}_page{i+1}_img{img_index+1}.{ext}"
#             image_path = f"temp_{image_name}"
#             image.save(image_path)
#             images.append((image_path, image_name))
#     return images
#
# def load_documents(folder_path):
#     docs = []
#
#     for file in os.listdir(folder_path):
#         path = os.path.join(folder_path, file)
#
#         if file.lower().endswith(".pdf"):
#             print(f"📄 Loading PDF: {file}")
#             loader = PyMuPDFLoader(path)
#             docs.extend(loader.load())
#
#             print(f"🖼️ Extracting images from PDF: {file}")
#             images = extract_images_from_pdf(path)
#             for img_path, img_name in images:
#                 extracted = extract_text_from_image_with_gpt(img_path)
#                 docs.append(Document(page_content=extracted, metadata={"source": img_name}))
#                 os.remove(img_path)
#
#         elif file.lower().endswith((".png", ".jpg", ".jpeg")):
#             print(f"🖼️ Loading image: {file}")
#             extracted = extract_text_from_image_with_gpt(path)
#             docs.append(Document(page_content=extracted, metadata={"source": file}))
#
#     return docs
#
# # if __name__ == "__main__":
# #     folder = "../docs"
# #     docs = load_documents(folder)
# #
# #     print("\n✅ Displaying sample outputs:")
# #     for i, doc in enumerate(docs[:3]):
# #         print(f"\n--- Document {i+1} ---")
# #         print(doc.page_content[:800])

