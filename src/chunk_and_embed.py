import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from doc_loader import load_documents
from dotenv import load_dotenv

load_dotenv()

INDEX_PATH = "faiss_index"

def chunk_documents(documents, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)

def load_or_create_index(chunks):
    embeddings = OpenAIEmbeddings()

    if os.path.exists(INDEX_PATH):
        print("📦 Loading existing FAISS index...")
        vectorstore = FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        if not chunks:
            raise ValueError("❌ No documents to index.")
        print("🆕 Creating new FAISS index...")
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(INDEX_PATH)
        print("✅ New FAISS index created.")

    return vectorstore, embeddings

def embed_and_add_new_docs(vectorstore, new_chunks, embeddings):
    print("➕ Adding new chunks to index...")
    vectorstore.add_documents(new_chunks)
    vectorstore.save_local(INDEX_PATH)
    print("✅ Index updated and saved.")


# 🧪 RUN
# if __name__ == "__main__":
#     folder_path = "../docs"
#     print("📥 Loading documents...")
#     raw_docs = load_documents(folder_path)
#
#     print("✂️ Chunking documents...")
#     chunks = chunk_documents(raw_docs)
#
#     # ✅ Just preview first few chunks
#     print("📄 Preview of first few chunks:")
#     for i, chunk in enumerate(chunks[:3]):
#         print(f"\n--- Chunk {i+1} ---")
#         print(chunk.page_content[:500])
#
#     print("📚 Loading or creating FAISS index...")
#     vectorstore, embeddings = load_or_create_index(chunks)
#
#     print("🔗 Adding new documents (no duplicates)...")
#     embed_and_add_new_docs(vectorstore, chunks, embeddings)

